import fitz  # PyMuPDF
from PIL import Image
import io
from transformers import CLIPProcessor, CLIPModel
from sentence_transformers import SentenceTransformer
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import hashlib

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
