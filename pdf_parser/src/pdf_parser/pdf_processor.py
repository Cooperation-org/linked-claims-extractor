import fitz  # PyMuPDF
from PIL import Image
import io
from transformers import CLIPProcessor, CLIPModel
from sentence_transformers import SentenceTransformer
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import hashlib
import nltk
from pdf2image import convert_from_path
import pytesseract
# import pdfplumber
import re
from nltk.tokenize import sent_tokenize
import spacy

# check punk_tab existence
if not nltk.data.find('tokenizers/punkt_tab'):
   nltk.download('punkt_tab')

# Load spaCy NLP model
nlp = spacy.load('en_core_web_sm')

@dataclass
class ProcessedChunk:
    content: str
    embedding: np.ndarray
    metadata: Dict[str, Any]
    chunk_id: str
    type: str = 'text'  # 'text' or 'image'

class PDFProcessor:
    def __init__(self):
        self.text_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    def process_pdf(self, pdf_path: str) -> List[ProcessedChunk]:
        """Process PDF and return chunks"""
        print(f"Processing PDF {pdf_path}...")
        return self._process_pdf_internal(pdf_path)

    def _process_pdf_internal(self, pdf_path: str) -> List[ProcessedChunk]:
        """Internal method for actual PDF processing"""
        processed_chunks = []
        doc = fitz.open(pdf_path)

        for page_num, page in enumerate(doc):
            print(f"Processing page {page_num + 1}/{doc.page_count}")
            # Process text
            text_blocks = page.get_text("blocks")
            for block in text_blocks:
                text = block[4]
                if len(text.strip()) < 10:
                    continue

                chunk = self._process_text_chunk(
                    text=text,
                    page=page_num,
                    bbox=block[:4]
                )
                processed_chunks.append(chunk)

            # Process images
            images = page.get_images(full=True)
            for img_index, img in enumerate(images):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image = Image.open(io.BytesIO(image_bytes))

                    chunk = self._process_image_chunk(
                        image=image,
                        page=page_num
                    )
                    processed_chunks.append(chunk)
                except Exception as e:
                    print(f"Error processing image on page {page_num}: {e}")
                    continue

        return processed_chunks

    def _generate_chunk_id(self, content: str, page: int, bbox: Optional[List] = None) -> str:
        """Generate a unique ID for a chunk based on content, position and bbox"""
        if bbox:
            # Include bbox in hash if available for text chunks
            unique_string = f"{content}_{page}_{bbox[0]}_{bbox[1]}_{bbox[2]}_{bbox[3]}"
        else:
            # For images, include a counter to ensure uniqueness
            unique_string = f"{content}_{page}_{hash(content)}"
        return hashlib.md5(unique_string.encode()).hexdigest()

    def _process_text_chunk(self, text: str, page: int, bbox: Optional[List] = None) -> ProcessedChunk:
        """Process a single text chunk"""
        embedding = self.text_model.encode(text)

        metadata = {
            'page': page,
            'type': 'text',
        }
        if bbox:
            metadata['bbox'] = bbox

        return ProcessedChunk(
            content=text,
            embedding=embedding,
            metadata=metadata,
            chunk_id=self._generate_chunk_id(text, page, bbox),  # Pass bbox to ID generation
            type='text'
        )

    def _process_image_chunk(self, image: Image.Image, page: int) -> ProcessedChunk:
        """Process a single image chunk"""
        inputs = self.clip_processor(images=image, return_tensors="pt")
        image_features = self.clip_model.get_image_features(**inputs)
        embedding = image_features.detach().numpy()[0]

        metadata = {
            'page': page,
            'type': 'image',
        }

        content = f"Image on page {page}"

        return ProcessedChunk(
            content=content,
            embedding=embedding,
            metadata=metadata,
            chunk_id=self._generate_chunk_id(content, page),
            type='image'
        )
    
    # clean and structure text
    def _clean_and_structure_text(self, text:str) -> Dict[str, Any]:
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
  
    # extract all text from pdf    
    def extract_text_from_pdf(self, pdf_path:str) -> Dict[str, Any]:
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
            
            processed_text = self._clean_and_structure_text(text)
            
    
        except Exception as e:
            print(f"Error extracting text: {e}")
    
        return processed_text

    # extract text from each page
    def extract_text_from_pdf_per_page(self, pdf_path:str) -> List[Dict[int, str]]:
        pages_text = []
        try:
            with fitz.open(pdf_path) as doc:
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    pages_text.append({page_num: self._clean_and_structure_text(page.get_text())['cleaned_text']})

            if not any(text.strip() for page_item in pages_text for _, text in page_item.items()):
                print("Attempting OCR...")
                images = convert_from_path(pdf_path)
                for page_num, image in enumerate(images):
                    img_text = pytesseract.image_to_string(image)
                    pages_text.append({page_num: self._clean_and_structure_text(img_text)['cleaned_text']})

        except Exception as e:
            print(f"Error: {e}")
            return []

        return pages_text