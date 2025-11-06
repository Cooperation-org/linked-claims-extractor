import json
import re
import logging
from typing import List, Dict, Any, Optional
import os
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.base import BaseLanguageModel
from .schemas.loader import load_schema_info, LINKED_TRUST

logger = logging.getLogger(__name__)

def default_llm():
    return ChatAnthropic(
        model=os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022"),
        temperature=0,
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

CRITICAL: Extract ONLY verifiable claims that describe COMPLETED actions with measurable outcomes.

EXTRACTION CRITERIA (ALL must be met):
1. Past tense verbs indicating completed action (provided, delivered, built, served, achieved, completed, reached, installed, distributed, implemented)
2. Quantifiable metrics showing measurable impact:
   - Numbers of people/families served (e.g., "45,000 people", "8,500 families")
   - Items delivered/built (e.g., "2,000 filters", "127 wells")
   - Percentages achieved (e.g., "95% vaccination coverage")
   - Amounts distributed (e.g., "$2M in aid")
   - NOT just location counts (e.g., "worked in 5 countries" ✗)
3. Clear timeframes (specific years, quarters, dates like "2024", "Q3 2023", "December 2024")
4. Concrete outcomes, not aspirations or plans

DO NOT EXTRACT:
- Future plans or intentions (will, plans to, going to, intends to, aims to, hopes to, expects to, working towards)
- Mission statements or values (we believe, committed to, our vision, our mission, dedicated to)
- Vague claims without specific numbers (many, several, improved, better, more)
- Conditional statements (could, might, would, if we)
- Process descriptions without outcomes (we are developing, we work on)

GOOD EXAMPLES TO EXTRACT:
✓ Water: "Provided clean water to 45,000 people in 2024"
✓ Infrastructure: "Built 127 wells serving 8,500 families in rural Kenya during 2023"
✓ Distribution: "Delivered 2,000 water filters to 15 communities in Q3"
✓ Health: "Reached 95% vaccination coverage in target regions by December 2024"
✓ Education: "Trained 1,250 teachers across 80 schools in 2023"
✓ Economic: "Distributed $2.5M in microloans to 5,000 entrepreneurs in FY2024"

BAD EXAMPLES - DO NOT EXTRACT:
✗ "We will expand to 5 new countries next year" (future tense)
✗ "We believe in clean water for all communities" (mission statement)
✗ "Plans to serve 10,000 more families" (future plan)
✗ "Working to improve water access" (vague, no specific outcome)
✗ "Our mission is to end water scarcity" (mission statement)
✗ "We are developing new filtration technology" (process, not outcome)
✗ "We could reach 100,000 people with more funding" (conditional)

DECISION FRAMEWORK:
For each potential claim, verify:
1. Is the action COMPLETED (past tense)? → Must be YES
2. Are there SPECIFIC NUMBERS (not "many")? → Must be YES  
3. Is there a CLEAR TIMEFRAME (not "recently")? → Must be YES
4. Is this an OUTCOME (not intention)? → Must be YES
If all 4 are YES → EXTRACT. If any is NO → SKIP.

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
        self.message_prompt = message_prompt
        if not re.search(r'\{text\}', message_prompt):
            self.message_prompt += " {text}"
        

    def make_prompt(self, prompt=None, override_prompt=False) -> ChatPromptTemplate:
        """Prepare the prompt - for now this is static, later may vary by type of claim"""

        if prompt is None:
            prompt = self.system_template

        logging.info(f"*** system_prompt = {self.system_template}")
        if override_prompt:
            logging.info(f"*** Overriding system prompt: {prompt}")
#            logging.info(f"*** Overriding system prompt! ***")
            message_list = [
                SystemMessagePromptTemplate.from_template(prompt),
                HumanMessagePromptTemplate.from_template("""Here is a narrative about some impact.
                Please extract any specific claims: {text}"""),
            ]
        else:
            prompt += " {text}"
            logging.info(f"*** Original non-system prompt: {prompt}")
            message_list = [
                SystemMessagePromptTemplate.from_template(self.system_template),
                HumanMessagePromptTemplate.from_template(prompt)
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
        logging.info(f"*** TEXT = {text}")
        messages = prompt_template.format_messages(text=text)

        logging.info(f"*** MESSAGES = {messages}")

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
        import requests
        logger.debug(f"Fetching content from URL: {url}")
        response = requests.get(url)
        response.raise_for_status()

        logger.info(f"Successfully retrieved content (length: {len(response.text)} characters)")
        return self.extract_claims(response.text)
