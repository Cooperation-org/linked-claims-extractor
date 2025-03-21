import nltk
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract
import pdfplumber
import re
from nltk.tokenize import sent_tokenize
import spacy
import openai
import os
import requests
import json
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.base_language import BaseLanguageModel

nltk.download('punkt_tab')

# Load spaCy NLP model
nlp = spacy.load('en_core_web_sm')

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file, handling both text-based and scanned PDFs.
    """
    text = ""

    try:
        # Attempt to extract text directly using PyMuPDF
        with fitz.open(pdf_path) as doc:
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()

        # If no text is extracted, assume it's a scanned PDF and use OCR
        if not text.strip():
            print("No text found. Attempting OCR...")
            images = convert_from_path(pdf_path, dpi=300)
            for image in images:
                text += pytesseract.image_to_string(image)

    except Exception as e:
        print(f"Error extracting text: {e}")

    return text

def extract_tables_from_pdf(pdf_path):
    """
    Extracts tables from a PDF file using pdfplumber.
    """
    tables = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
    except Exception as e:
        print(f"Error extracting tables: {e}")

    return tables

def clean_and_structure_text(text):
    """
    Cleans and structures the extracted text.
    """
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text).strip()

    # Tokenize into sentences
    sentences = sent_tokenize(text)

    # Use spaCy for further processing (e.g., entity recognition)
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]

    return {
        'cleaned_text': text,
        'sentences': sentences,
        'entities': entities
    }

# def save_to_file(filename, data):
    """
    Saves data to a text file.
    """
    with open(filename, 'w', encoding='utf-8') as file:
        if isinstance(data, list):
            for item in data:
                if isinstance(item, (list, tuple)):
                    file.write(", ".join(map(str, item)) + "\n")
                else:
                    file.write(str(item) + "\n")
        else:
            file.write(str(data))

    

prompt = """You are a JSON claim extraction specialist. Your task is to analyze input text and identify factual claims matching the following schema:
        {{
  "subject": "string",
  "claim": "string",
  "object": "string",
  "statement": "string",
  "aspect": "string",
  "amt": 0,
  "name": "string",
  "howKnown": "FIRST_HAND",
  "images": [
    {{
      "url": "string",
      "metadata": {{
        "captian": "string",
        "description": "string"
      }},
      "effectiveDate": "2024-11-07T21:23:25.596Z",
      "digestMultibase": "string",
      "signature": "string",
      "owner": "string"
    }}
  ],
  "sourceURI": "string",
  "effectiveDate": "2024-11-07T21:23:25.596Z",
  "confidence": 0,
  "claimAddress": "string",
  "stars": 0
}}


        Meta Context for Claims:
        
claim: one of 'impact', 'rated', 'same_as'
aspect: similar to 'impact:financial', 'impact:social', 'impact:work', 'quality:overall', 'quality:affordable', 'quality:fun', 'report:scam', 'report:dangerous'
howKnown: will be set by the caller later
effectiveDate: when the impact or rating occurred, if you can tell
object: only if it has a url
subject: try to find a url (may not be possible), otherwise use text
statement: this is the concise narrative of the claim, quoted from the text
amt: optional, generally only for impact claims and only if an amount is present.  The total impact claimed.
unit: include if amt is set ; usd if dollars, or set according to what amt is counting
stars: optional if claim is a rating, scale is 1-5, otherwise leave out of the result
score: if claim is a rating, may be set from -1 to 1 as a float, otherwise unset.  5 stars = score of 1


        Instructions:
        1. Thoroughly examine the provided text while cross-referencing the schema requirements
        2. Only extract claims that are explicitly stated or strongly implied in the text
        3. Maintain strict adherence to the defined schema structure
        4. If no claims match the criteria, return an empty array []
        5. Never invent claims or use external knowledge
        6. Prioritize precision over quantity

        Output Guidelines:
        - ALWAYS output a valid JSON array (starting with [ and ending with ])
        - NEVER include markdown formatting or code blocks
        - NEVER add explanations, disclaimers, or non-JSON content
        - Ensure proper JSON syntax and escaping
        - Maintain case sensitivity as defined in the schema

        Response must be exclusively the JSON array with no additional text.

"""
API_KEY = os.getenv("ANTHROPIC_API_KEY")

API_URL = "https://api.anthropic.com/v1/messages"
def send_prompt_to_claude(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
        "Anthropic-Version": "2024-02-29" 
    }

    data = {
        "model": "claude-3-sonnet-20240229",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 1000  
    }

    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()  
    else:
        return f"Error: {response.status_code}, {response.text}"

def process_pdf(pdf_path):  # output_prefix, out_path
    """
    Main function to process a PDF file and save results to separate files.
    """
    # Step 1: Extract text
    text = extract_text_from_pdf(pdf_path)

    # Step 2: Extract tables (if any)
    tables = extract_tables_from_pdf(pdf_path)

    # Step 3: Clean and structure the text
    processed_text = clean_and_structure_text(text)

    # Step 4: Save results to separate files
    # save_to_file(f"{main_path+output_prefix}_text.txt", processed_text['cleaned_text'])
    # save_to_file(f"{main_path+output_prefix}_sentences.txt", processed_text['sentences'])
    # save_to_file(f"{main_path+output_prefix}_entities.txt", processed_text['entities'])
    # save_to_file(f"{main_path+output_prefix}_tables.txt", tables)

    # print(f"Results saved to {output_prefix}_*.txt files.")
    return text, tables, processed_text

def main(pdf_path, prompt):
    _, _, processed_text = process_pdf(pdf_path)
    prompt += "\n".join(processed_text["sentences"])    
    claims = send_prompt_to_claude(prompt)
    return claims
    # print(claims)
    # Initialize document manager
    # doc_manager = DocumentManager()
    
    # # Process PDF
    # doc_manager.process_pdf(pdf_path, reset=args.reset)
    
    # # Start REPL
    # repl = DocumentREPL(doc_manager=doc_manager)
    # repl.cmdloop()
# Example usage
if __name__ == "__main__":
  pdf_path =  "/content/drive/MyDrive/claim-extractor/goalkeeper-2024.pdf"
  main(pdf_path, prompt)


# def default_llm():
#     return  ChatAnthropic(
#                model="claude-3-sonnet-20240229",  # This is the current Sonnet model
#                temperature=0,  # 0 to 1, lower means more deterministic
#                max_tokens=4096)


# llm = default_llm()