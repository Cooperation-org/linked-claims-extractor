import json
import re
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
        (self.schema, self.meta, self.post_processor)  = load_schema_info(schema_name)
        self.llm = llm or default_llm()
        self.system_template = f"""You are a claim extraction assistant that outputs raw json claims in a json array. You analyze text and extract claims according to this schema:
        {self.schema}
        Consider this meta information when filling the fields

        {self.meta}
        
        Output format: Return ONLY a JSON array of claims with no explanatory text, no preamble, and no other content. The output must start with [ and end with ]. 

        """

        
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
        try:
            response = self.llm(messages)
        except TypeError as e:
            logging.error(f"Failed to authenticate: {str(e)}.  Do you need to use dotenv in caller?")
        try:
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            # sometimes the LLM insists on prepending some text
            m = re.match(r'[^\[]+(\[[^\]]+\])[^\]]*$', response.content)
            if m:
                try:
                    return json.loads(m.group(1))
                except json.JSONDecodeError as e:
                    pass 
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
