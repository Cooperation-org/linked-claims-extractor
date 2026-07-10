import json
import re
import logging
from typing import List, Dict, Any, Optional
import os
import requests
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.base import BaseLanguageModel
from .schemas.loader import load_schema_info, LINKED_TRUST

logger = logging.getLogger(__name__)

# claude-3-5-sonnet-20241022 was retired 2025-10-28; claude-sonnet-5 is its
# documented drop-in replacement. Sonnet 5 rejects non-default sampling
# parameters, so temperature must not be set here.
DEFAULT_CLAUDE_MODEL = "claude-sonnet-5"

# Default human message when no message_prompt is configured.
DEFAULT_MESSAGE_TEMPLATE = """Here is a narrative about some impact.
                Please extract any specific claims: {text}"""

def default_llm():
    return ChatAnthropic(
        model=os.getenv("CLAUDE_MODEL", DEFAULT_CLAUDE_MODEL),
        max_tokens=int(os.getenv("CLAUDE_MAX_TOKENS", 4096)))

class ClaimExtractor:
    def __init__(
        self, 
        llm: Optional[BaseLanguageModel] = None,
        schema_name: str = LINKED_TRUST,
        extra_system_instructions: Optional[str] = '',
        message_prompt: Optional[str] = None
    ):
        """
        Initialize claim extractor with specified schema and LLM.
        
        Args:
            llm: Language model to use (ChatOpenAI, ChatAnthropic, etc). If None, uses ChatOpenAI
            schema_name: Schema identifier or path/URL to use for extraction
            temperature: Temperature setting for the LLM if creating default
        """
        self.schema, self.meta = load_schema_info(schema_name)
        self.llm = llm or default_llm()
        self.system_template = f"""
        You are a JSON claim extraction specialist extracting LinkedClaims (https://identity.foundation/labs-linkedclaims/).
        Extract claims matching this schema:
        {self.schema}

        Meta Context:
        {self.meta}

        CRITICAL REQUIREMENTS:
        0. DO NOT GUESS. ONLY extract information actually in the provided text.
        1. If a field must be a URI but a clear URI does not exist in the text, construct appropriate URIs using 'urn:' prefix
        2. Return empty array [] if no valid claims found

        {extra_system_instructions} Additional requirements may be in the message prompt.

        Output: Valid JSON array only, no markdown or explanations.
        """
        if message_prompt is not None and not re.search(r'\{text\}', message_prompt):
            message_prompt += " {text}"
        self.message_prompt = message_prompt

    def make_prompt(self, prompt=None, override_prompt=False) -> ChatPromptTemplate:
        """Prepare the prompt - for now this is static, later may vary by type of claim"""

        default_message = self.message_prompt or DEFAULT_MESSAGE_TEMPLATE

        if override_prompt and prompt is not None:
            logger.info(f"*** Overriding system prompt: {prompt}")
            system = prompt
            message = default_message
        else:
            system = self.system_template
            if prompt is not None:
                if not re.search(r'\{text\}', prompt):
                    prompt += " {text}"
                message = prompt
            else:
                message = default_message

        message_list = [
            SystemMessagePromptTemplate.from_template(system),
            HumanMessagePromptTemplate.from_template(message),
        ]
        return ChatPromptTemplate.from_messages(message_list)

    
    def extract_claims(self, text: str, prompt=None, override_prompt=False) -> List[Dict[str, Any]]:
        """
        Extract claims from the given text.
        
        Args:
            text: Text to extract claims from
            override_prompt: If true, prompt replaces the system prompt, rather than being appended
            
        Returns:
            List[Dict[str, Any]]: JSON array of extracted claims
        """
        prompt_template = self.make_prompt(prompt, override_prompt)

        # Format messages with the text
        logger.debug(f"*** TEXT = {text}")
        messages = prompt_template.format_messages(text=text)

        logger.debug(f"*** MESSAGES = {messages}")

        response = None
        try:
            logger.debug(f"Sending request to LLM: {messages}")
            response = self.llm.invoke(messages)
            logger.info(f"Received response from LLM (length: {len(response.content) if response else 0} characters)")
        except TypeError as e:
            logger.error(f"Failed to authenticate: {str(e)}. Do you need to use dotenv in caller?")
            return []
        except Exception as e:
            logger.error(f"Error invoking LLM: {str(e)}")
            return []
            
        if response:
            try:
                parsed_response = json.loads(response.content)
                logger.info(f"Successfully parsed JSON response with {len(parsed_response)} claims")
                return parsed_response
            except json.JSONDecodeError as e:
                logger.info(f"JSON decode error: {str(e)}")
                
                # Try to extract JSON array from response if it's surrounded by other text
                m = re.match(r'[^\[]+(\[[^\]]+\])[^\]]*$', response.content)
                if m:
                    try:
                        extracted_json = json.loads(m.group(1))
                        logger.info(f"After cleaning, successfully extracted JSON from response with {len(extracted_json)} claims")
                        return extracted_json
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse extracted JSON: {str(e)}")
                
                logger.debug(f"Response content preview: {response.content[:500]}")
        
        logger.info("No claims extracted, returning empty list")
        return []

    def extract_claims_from_url(self, url: str) -> List[Dict[str, Any]]:
        """
        Extract claims from text at URL.
        
        Args:
            url: URL to fetch text from
            
        Returns:
            List[Dict[str, Any]]: JSON array of extracted claims
        """
        logger.debug(f"Fetching content from URL: {url}")
        response = requests.get(url)
        response.raise_for_status()

        logger.info(f"Successfully retrieved content (length: {len(response.text)} characters)")
        return self.extract_claims(response.text)
