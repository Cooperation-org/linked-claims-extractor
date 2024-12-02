from pathlib import Path
from typing import List, Dict, Any
from .pdf_processor import PDFProcessor
from .cache_manager import PDFProcessingCache, ChromaDBManager
import chromadb

class DocumentManager:
    def __init__(self, collection_name: str = "documents", 
             persist_dir: str = ".chromadb",
             cache_dir: str = ".cache"):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.db_manager = ChromaDBManager(persist_dir)
        self.text_collection = self.db_manager.get_or_create_collection(f"{collection_name}_text")
        self.image_collection = self.db_manager.get_or_create_collection(f"{collection_name}_images")
        self.cache = PDFProcessingCache(cache_dir)
        self.processor = PDFProcessor()

    def reset_collection(self):
        """Completely reset the ChromaDB collections"""
        print(f"Resetting ChromaDB collections {self.collection_name}_text and {self.collection_name}_images...")
        self.db_manager.delete_collection(f"{self.collection_name}_text")
        self.db_manager.delete_collection(f"{self.collection_name}_images")
        self.text_collection = self.db_manager.get_or_create_collection(f"{self.collection_name}_text")
        self.image_collection = self.db_manager.get_or_create_collection(f"{self.collection_name}_images")
        print("ChromaDB collections reset complete")

    def process_pdf(self, pdf_path: str, reset: bool = False):
        """Process PDF and add to collections"""
        if reset:
            self.reset_collection()
            self.cache.reset()
            
        pdf_name = Path(pdf_path).stem

        # Check if we need to process
        if not self.cache.needs_processing(pdf_path, pdf_name):
            print(f"Using existing ChromaDB data for {pdf_name}")
            return
        
        print(f"\nProcessing {pdf_path}:")
        print("1. Processing PDF and generating embeddings...")
        chunks = self.processor.process_pdf(pdf_path)
        print(f"   Generated {len(chunks)} chunks")
        
        print("2. Preparing data for ChromaDB...")
        metadatas = []
        for chunk in chunks:
            metadata = chunk.metadata.copy()
            if 'bbox' in metadata:
                x1, y1, x2, y2 = metadata['bbox']
                metadata['bbox_left'] = x1
                metadata['bbox_top'] = y1
                metadata['bbox_right'] = x2
                metadata['bbox_bottom'] = y2
                del metadata['bbox']
            metadata['source_document'] = pdf_name
            metadatas.append(metadata)
        
        print(f"3. Adding chunks to ChromaDB collections...")
        for i, chunk in enumerate(chunks):
            try:
                collection = self.text_collection if chunk.type == 'text' else self.image_collection
                collection.add(
                    embeddings=[chunk.embedding.tolist()],
                    ids=[f"{pdf_name}_{chunk.chunk_id}"],
                    documents=[chunk.content],
                    metadatas=[metadatas[i]]
                )
            except chromadb.errors.DuplicateIDError:
                print(f"Skipping duplicate chunk: {chunk.content[:100]}...")
        
        # Update cache
        self.cache.update_metadata(pdf_path, pdf_name)
        print("Processing complete!")

    def query(self, query_text: str, n_results: int = 3):
        """Query across all documents in collections"""
        # Get text embeddings for text collection
        text_embedding = self.processor.text_model.encode(query_text)
        text_results = self.text_collection.query(
            query_embeddings=[text_embedding.tolist()],
            n_results=n_results
        )
        
        # Get CLIP embeddings for image collection using the text encoder
        inputs = self.processor.clip_processor(text=query_text, return_tensors="pt")
        image_query_embedding = self.processor.clip_model.get_text_features(**inputs)
        image_results = self.image_collection.query(
            query_embeddings=[image_query_embedding.detach().numpy()[0].tolist()],
            n_results=n_results
        )
        
        formatted_results = []
        
        # Add text results
        for i in range(len(text_results['documents'][0])):
            formatted_results.append({
                'content': text_results['documents'][0][i],
                'metadata': text_results['metadatas'][0][i],
                'distance': text_results['distances'][0][i]
            })
        
        # Add image results
        for i in range(len(image_results['documents'][0])):
            formatted_results.append({
                'content': image_results['documents'][0][i],
                'metadata': image_results['metadatas'][0][i],
                'distance': image_results['distances'][0][i]
            })
        
        # Sort by distance and limit to n_results
        formatted_results.sort(key=lambda x: x['distance'])
        return formatted_results[:n_results]
