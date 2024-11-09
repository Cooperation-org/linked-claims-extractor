import json
import logging
from typing import List, Dict, Any, Optional, Union

from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.base_language import BaseLanguageModel

from .schemas.loader import load_schema_info, LINKED_TRUST

def default_llm():
    return  ChatAnthropic(
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
        (self.schema, self.meta)  = load_schema_info(schema_name)
        self.llm = llm or default_llm()
        self.system_template = f"""You are a claim extraction assistant that outputs raw json claims in a json array. You analyze text and extract claims according to this schema:
        {self.schema}
        With no explanation, return extracted claims in a valid json array.  Consider this meta information

        {self.meta}

        when filling the fields.  Remember to return just the bare extracted claims in a valid json array"""
        
    def make_prompt(self) -> ChatPromptTemplate:
        """Prepare the prompt - for now this is static, later may vary by type of claim"""
        human_template = """Here is a narrative about some impact. Please extract any specific claims:
        {text}"""
        
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
    
    def extract_claims(self, text: str) -> List[dict[str, Any]]:
        """
        Extract claims from the given text.
        
        Args:
            text: Text to extract claims from
            
        Returns:
            str: JSON array of extracted claims
        """
        prompt = self.make_prompt()
        messages = prompt.format_messages(text=text)
        response = self.llm(messages)
        try:
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            logging.info(f"Failed to parse LLM response as JSON: {response.content}")
            return []
    
    def extract_claims_from_url(self, url: str) -> str:
        """
        Extract claims from text at URL.
        
        Args:
            url: URL to fetch text from
            
        Returns:
            str: JSON array of extracted claims
        """
        import requests
        response = requests.get(url)
        response.raise_for_status()
        return self.extract_claims(response.text)
