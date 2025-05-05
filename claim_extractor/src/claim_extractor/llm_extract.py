import json
import re
import logging
from typing import List, Dict, Any, Optional

from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain.base_language import BaseLanguageModel

from .schemas.loader import load_schema_info, LINKED_TRUST

def default_llm():
    return ChatAnthropic(
        model="claude-3-sonnet-20240229",  # This is the current Sonnet model
        temperature=0,  # 0 to 1, lower means more deterministic
        max_tokens=4096)

class ClaimExtractor:
    def __init__(
        self, 
        llm: Optional[BaseLanguageModel] = None,
        schema_name: str = LINKED_TRUST 
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
        You are a JSON claim extraction specialist. Your task is to analyze input text and identify factual claims that can be proven true or false through evidence matching the following schema:
        {self.schema}

        Meta Context for Claims:
        {self.meta}

        Instructions:
        1. Focus only on extracting claims that can be verified with evidence
        2. Thoroughly examine the provided text while cross-referencing the schema requirements
        3. Only extract claims that are explicitly stated or strongly implied in the text
        4. Maintain strict adherence to the defined schema structure
        5. If no claims match the criteria, return an empty array []
        6. Never invent claims or use external knowledge
        7. Prioritize precision over quantity
        8. If the text contains formatting artifacts or appears to be a fragment from a PDF, carefully analyze it to identify any verifiable claims despite these issues
        

        Output Guidelines:
        - ALWAYS output a valid JSON array (starting with [ and ending with ])
        - NEVER include markdown formatting or code blocks
        - NEVER add explanations, disclaimers, or non-JSON content
        - Ensure proper JSON syntax and escaping
        - Maintain case sensitivity as defined in the schema

        Response must be exclusively the JSON array with no additional text.
        Text:
        
        """
        

    def make_prompt(self, prompt=None) -> ChatPromptTemplate:
        """Prepare the prompt - for now this is static, later may vary by type of claim"""
        if prompt is None:
            prompt = self.system_template
            
        if prompt:
            prompt += " {text}"
        else:
            prompt = """Here is a narrative about some impact. Please extract any specific claims:
        {text}"""

        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.system_template),
            HumanMessagePromptTemplate.from_template(prompt)
        ])

    # def print_messages(self, messages):
    #     """Print formatted messages for debugging"""
    #     print("\n=== PROMPT MESSAGES ===")
    #     for i, message in enumerate(messages):
    #         if message.type == 'human':
    #             print(f"Message {i+1} ({message.type}):")
    #             print(message.content)
    #             print("-" * 60)
    #     print("=== END PROMPT MESSAGES ===\n")

    # def print_response(self, response):
    #     """Print formatted response for debugging"""
    #     print("\n=== LLM RESPONSE ===")
    #     print(response.content)
    #     print("=== END LLM RESPONSE ===\n")
    
    def extract_claims(self, text: str, prompt=None) -> List[Dict[str, Any]]:
        """
        Extract claims from the given text.
        
        Args:
            text: Text to extract claims from
            
        Returns:
            List[Dict[str, Any]]: JSON array of extracted claims
        """
        prompt_template = self.make_prompt(prompt)
        
        # Format messages with the text
        messages = prompt_template.format_messages(text=text)
        # self.print_messages(messages)
        response = None
        try:
            print("Sending request to LLM...")
            response = self.llm.invoke(messages)
            print(f"Received response from LLM (length: {len(response.content) if response else 0} characters)")
        except TypeError as e:
            logging.error(f"Failed to authenticate: {str(e)}. Do you need to use dotenv in caller?")
            return []
        except Exception as e:
            logging.error(f"Error invoking LLM: {str(e)}")
            return []
            
        if response:
            try:
                # Print the response to debug
                # self.print_response(response)
                parsed_response = json.loads(response.content)
                print(f"Successfully parsed JSON response with {len(parsed_response)} claims")
                return parsed_response
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {str(e)}")
                
                # Try to extract JSON array from response if it's surrounded by other text
                m = re.match(r'[^\[]+(\[[^\]]+\])[^\]]*$', response.content)
                if m:
                    try:
                        extracted_json = json.loads(m.group(1))
                        print(f"Successfully extracted JSON from response with {len(extracted_json)} claims")
                        return extracted_json
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse extracted JSON: {str(e)}")
                
                print("Response content preview:")
                print(response.content[:500] + "..." if len(response.content) > 500 else response.content)
                logging.info(f"Failed to parse LLM response as JSON: {response.content}")
        
        print("No claims extracted, returning empty list")
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
        print(f"Fetching content from URL: {url}")
        response = requests.get(url)
        response.raise_for_status()
        print(f"Successfully retrieved content (length: {len(response.text)} characters)")
        return self.extract_claims(response.text)