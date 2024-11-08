from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_community.chat_models import ChatOpenAI, ChatAnthropic
from langchain.base_language import BaseLanguageModel
from typing import Optional, Union
from .schemas.loader import load_raw_schema, LINKED_TRUST

class ClaimExtractor:
    def __init__(
        self, 
        llm: Optional[BaseLanguageModel] = None,
        schema_name: str = LINKED_TRUST, 
        temperature: float = 0
    ):
        """
        Initialize claim extractor with specified schema and LLM.
        
        Args:
            llm: Language model to use (ChatOpenAI, ChatAnthropic, etc). If None, uses ChatOpenAI
            schema_name: Schema identifier or path/URL to use for extraction
            temperature: Temperature setting for the LLM if creating default
        """
        self.schema = load_raw_schema(schema_name).replace("{", "{{").replace("}", "}}")
        self.llm = llm or ChatOpenAI(temperature=temperature)
        self.system_template = f"""You are a claim extraction assistant. You analyze text and extract claims according to this schema:
        {self.schema}
        For each claim you identify, structure it according to the given schema above, returning them in a json array."""
        
    def make_prompt(self) -> ChatPromptTemplate:
        """Prepare the prompt - for now this is static, later may vary by type of claim"""
        human_template = """Here is a narrative about some impact. Please extract any specific claims:
        {text}"""
        
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
    
    def extract_claims(self, text: str) -> str:
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
        return response.content
    
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
