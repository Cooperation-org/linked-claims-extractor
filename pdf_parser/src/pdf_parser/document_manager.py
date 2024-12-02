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
        self.collection = self.db_manager.get_or_create_collection(collection_name)
        self.cache = PDFProcessingCache(cache_dir)
        self.processor = PDFProcessor()

    def reset_collection(self):
        """Completely reset the ChromaDB collection"""
        print(f"Resetting ChromaDB collection {self.collection_name}...")
        self.db_manager.delete_collection(self.collection_name)
        self.collection = self.db_manager.get_or_create_collection(self.collection_name)
        print("ChromaDB collection reset complete")
    
    
    def process_pdf(self, pdf_path: str, reset: bool = False):
        """Process PDF and add to collection"""
        if reset:
            self.reset_collection()
            
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
        embeddings = [chunk.embedding.tolist() for chunk in chunks]
        ids = [f"{pdf_name}_{chunk.chunk_id}" for chunk in chunks]
        documents = [chunk.content for chunk in chunks]

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

        
        print(f"3. Adding chunks to ChromaDB collection {self.collection_name}...")
        try:
            self.collection.add(
                embeddings=embeddings,
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
        except chromadb.errors.DuplicateIDError as e:
            # Extract duplicate IDs from error message
            dupes = str(e).split("duplicates of: ")[1].split(" in add")[0].split(", ")
            print("\nWarning: Found duplicate chunks:")
            for dupe_id in dupes:
                # Find the chunk's index
                try:
                    idx = ids.index(dupe_id)
                    print(f"Page {chunks[idx].metadata['page']}: {documents[idx][:100]}...")
                except:
                    print(f"Duplicate ID: {dupe_id}")
            print("\nSkipping duplicates and continuing...")
        
        # Update cache
        self.cache.update_metadata(pdf_path, pdf_name)
        print("Processing complete!")

    def query(self, query_text: str, n_results: int = 3):
        """Query across all documents in collection"""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })
        
        return formatted_results
