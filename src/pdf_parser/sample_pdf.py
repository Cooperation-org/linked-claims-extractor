from dotenv import load_dotenv
import os
from anthropic import Anthropic
from typing import List, Tuple
from chromadb.utils import embedding_functions
import chromadb
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import numpy as np

from proc_pdf import PDFProcessor

class LocalRAG:
    def __init__(self, collection_name="pdf_store"):
        load_dotenv()
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Initialize Chroma
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        
        # Use sentence-transformers embeddings
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name='all-MiniLM-L6-v2'
        )
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )
        
        # For BM25 hybrid search
        self.text_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.bm25 = None
        self.documents = []
    
    def add_documents(self, processed_docs):
        """Add processed PDF data to Chroma"""
        ids = []
        texts = []
        metadatas = []
        
        for i, doc in enumerate(processed_docs):
            ids.append(f"doc_{i}")
            texts.append(doc.content)
            metadatas.append({
                'type': doc.type,
                'page': doc.metadata.get('page', '0'),
                'bbox': str(doc.metadata.get('bbox', ''))  # Convert bbox to string for storage
            })
        
        # Add to Chroma
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        # Update BM25 index for hybrid search
        self.documents = texts
        tokenized_docs = [doc.split() for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_docs)
    
    def hybrid_search(self, query: str, k: int = 5) -> List[dict]:
        # Vector search using Chroma
        vector_results = self.collection.query(
            query_texts=[query],
            n_results=k
        )
        
        # Keyword search using BM25
        tokenized_query = query.split()
        keyword_scores = self.bm25.get_scores(tokenized_query)
        top_keyword_indices = np.argsort(keyword_scores)[-k:][::-1]
        
        # Combine results
        results = set()
        
        # Add vector search results
        for doc, metadata in zip(vector_results['documents'][0], vector_results['metadatas'][0]):
            results.add((
                doc,
                metadata['type'],
                metadata['page']
            ))
        
        # Add keyword search results
        for idx in top_keyword_indices:
            results.add((
                self.documents[idx],
                'text',  # Default to text type for BM25 results
                0       # Default page
            ))
        
        return list(results)
    
    def query_document(self, question: str) -> str:
        # Get relevant chunks using hybrid search
        results = self.hybrid_search(question, k=5)
        
        # Format context
        context = self._format_context(results)
        
        # Query Claude
        message = self.anthropic.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            temperature=0,
            messages=[{
                "role": "user",
                "content": f"""Using only the context below, answer this question: {question}
                
                Context:
                {context}
                
                Answer the question based solely on the context provided. If the context doesn't contain enough information to answer fully, say so."""
            }]
        )
        
        return message.content

    def _format_context(self, results: List[Tuple[str, str, int]]) -> str:
        context_parts = []
        for content, type_, page in results:
            if type_ == 'text':
                context_parts.append(f"Text content: {content}")
            else:  # image
                context_parts.append(f"Image on page {page}: {content}")
        return "\n\n".join(context_parts)

# Usage example
def main():
    # Initialize RAG and PDF processor
    rag = LocalRAG()
    pdfproc = PDFProcessor()
    
    # Process PDF and add to Chroma
    print("Preprocessing the pdf...")
    pdf_data = pdfproc.process_pdf("goalkeeper-2024.pdf")  # Using the process_pdf function from earlier
    rag.add_documents(pdf_data)
    
    # Query examples
    questions = [
        "What are the main points in the executive summary?",
        "Are there any diagrams showing the system architecture?",
        "What are the key recommendations in the conclusion?"
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        print(f"Answer: {rag.query_document(question)}")
        print("-" * 80)

if __name__ == "__main__":
    main()
