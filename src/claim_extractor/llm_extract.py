import json
import re
import logging
from typing import List, Dict, Any, Optional
import os
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain.base_language import BaseLanguageModel
from .schemas.loader import load_schema_info, LINKED_TRUST

def default_llm():
    return ChatAnthropic(
        model=os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022"),
        temperature=0,
        max_tokens=int(os.getenv("CLAUDE_MAX_TOKENS", 4096)))

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
        
        # Define future tense words for filtering
        self.future_words = [
            "will", "plans", "exploring", "aims", "hopes", "seeks", "intends",
            "could", "would", "may", "might", "potential", "possibly",
            "future", "upcoming", "planned", "next year", "in the future",
            "working to", "trying to", "seeking to", "looking to"
        ]
        
        # Define mission statement indicators
        self.mission_indicators = [
            "bringing", "providing", "ensuring", "mission", "vision",
            "committed to", "dedicated to", "our goal", "we believe"
        ]
        
        self.system_template = f"""
        You are a JSON claim extraction specialist. Your task is to analyze input text and identify factual claims that can be proven true or false through evidence matching the following schema:
        {self.schema}

        Meta Context for Claims:
        {self.meta}

        Instructions:
        CRITICAL: You must NEVER extract any statement containing these words:
        - "will", "plans", "exploring", "aims", "hopes", "seeks"
        - "could", "would", "may", "might", "potential"
        - "future", "upcoming", "planned", "intends"

        STEP 1: Before extracting ANY claim, check if it contains future tense words above
        STEP 2: If it contains ANY future tense words, REJECT the entire statement
        STEP 3: ONLY extract claims about actions that ALREADY HAPPENED with past tense verbs

        1. Focus ONLY on extracting claims about COMPLETED, measurable outcomes with past tense verbs
        2. IMMEDIATELY SKIP any statement containing future tense indicators
        3. IMMEDIATELY SKIP broad mission statements or organizational purposes
        4. PRIORITIZE claims with:
                - Specific numbers, quantities, dates
                - Past tense action verbs ("built", "trained", "provided", "reduced")
                - Concrete locations and timeframes
        5. PRIORITIZE claims that someone could verify by:
                - Visiting the location and counting/measuring
                - Contacting specific people mentioned
                - Checking records from a specific time period
        6. If a sentence mixes completed outcomes with future projections, extract ONLY the completed portion
        7. If no verifiable completed outcomes exist, return empty array []
        8. Never invent claims or use external knowledge

        ACCEPTABLE examples: "provided", "built", "trained", "reduced", "served"
        FORBIDDEN examples: ANY sentence with "will", "plans to", "aims to"

        EXTRACT these types of completed outcomes:
                - "Produced 110 liters of milk per day"
                - "Gained 20 new customers since training"
                - "Trained 500 farmers in hygiene practices"
                - "Reduced child mortality by 15% in three districts"
                - "Built 12 schools serving 3,000 students"
                - "Distributed 10,000 bed nets to families"
                - "Increased crop yields by 25% among participating farmers"
                - "Provided clean water access to 50 villages"
                - "Vaccinated 2,500 children against measles"

        SKIP these future/aspirational statements:
                - "Will provide access to 1,000 more people"
                - "Plans to build additional schools"
                - "Exploring adding folic acid to salt"
                - "Has potential to reduce deaths by 75%"
                - "Working to improve healthcare access"
                - "No complaints about quality"
                - "Planning to expand program"
                - "Aims to improve healthcare"
                - "Could prevent up to 5,000 deaths"
                - "May help reduce poverty"

        REJECT broad organizational mission statements
        REJECT any claim mixing past achievements with future projections

        Output Guidelines:
        - ALWAYS output a valid JSON array (starting with [ and ending with ])
        - NEVER include markdown formatting or code blocks
        - NEVER add explanations, disclaimers, or non-JSON content
        - Ensure proper JSON syntax and escaping
        - Maintain case sensitivity as defined in the schema

        Response must be exclusively the JSON array with no additional text.
        Text:

        """

    def _contains_future_words(self, text: str) -> bool:
        """Check if text contains future tense indicators"""
        text_lower = text.lower()
        return any(word in text_lower for word in self.future_words)
    
    def _contains_mission_indicators(self, text: str) -> bool:
        """Check if text contains mission statement indicators"""
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in self.mission_indicators)
    
    def _is_vague_claim(self, text: str) -> bool:
        """Check if claim is too vague to be verifiable"""
        vague_patterns = [
            "no complaints", "improved quality", "better results",
            "increased satisfaction", "enhanced performance"
        ]
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in vague_patterns)

    def _filter_claims(self, claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out unverifiable claims using multiple criteria"""
        filtered_claims = []
        
        for claim in claims:
            statement = claim.get("statement", "")
            if not statement:
                continue
                
            # Check for future tense words
            if self._contains_future_words(statement):
                print(f"FILTERED (future tense): {statement[:100]}...")
                continue
                
            # Check for mission statements
            if self._contains_mission_indicators(statement):
                print(f"FILTERED (mission statement): {statement[:100]}...")
                continue
                
            # Check for vague claims
            if self._is_vague_claim(statement):
                print(f"FILTERED (vague claim): {statement[:100]}...")
                continue
                
            # Check for past tense verbs (positive indicator)
            past_tense_verbs = [
                "built", "trained", "provided", "reduced", "served", "delivered",
                "created", "established", "implemented", "completed", "achieved",
                "distributed", "vaccinated", "treated", "educated", "improved"
            ]
            
            has_past_tense = any(verb in statement.lower() for verb in past_tense_verbs)
            has_numbers = re.search(r'\d+', statement)
            
            if has_past_tense or has_numbers:
                filtered_claims.append(claim)
                print(f"KEPT (verifiable): {statement[:100]}...")
            else:
                print(f"FILTERED (no verifiable indicators): {statement[:100]}...")
                
        return filtered_claims

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
                # Parse the JSON response
                parsed_response = json.loads(response.content)
                print(f"Successfully parsed JSON response with {len(parsed_response)} claims")
                
                # Apply post-processing filters
                print("Applying post-processing filters...")
                filtered_claims = self._filter_claims(parsed_response)
                
                print(f"Final result: {len(filtered_claims)} verifiable claims after filtering")
                return filtered_claims
                
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {str(e)}")

                # Try to extract JSON array from response if it's surrounded by other text
                m = re.match(r'[^\[]+(\[[^\]]+\])[^\]]*$', response.content)
                if m:
                    try:
                        extracted_json = json.loads(m.group(1))
                        print(f"Successfully extracted JSON from response with {len(extracted_json)} claims")
                        
                        # Apply post-processing filters
                        print("Applying post-processing filters...")
                        filtered_claims = self._filter_claims(extracted_json)
                        
                        print(f"Final result: {len(filtered_claims)} verifiable claims after filtering")
                        return filtered_claims
                        
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