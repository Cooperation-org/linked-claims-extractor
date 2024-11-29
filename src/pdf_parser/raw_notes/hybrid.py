from langchain import PromptTemplate, LLMChain
from langchain.llms import OpenAI
import pinecone
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import numpy as np

class SemanticRAG:
    def __init__(self, pinecone_key, openai_key, index_name):
        pinecone.init(api_key=pinecone_key)
        self.index = pinecone.Index(index_name)
        self.llm = OpenAI(api_key=openai_key)
        self.text_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Cache for BM25
        self.documents = []
        self.bm25 = None
        self.initialize_keyword_search()
    
    def initialize_keyword_search(self):
        # Fetch all documents for keyword search
        fetch_response = self.index.fetch(ids=self.index.describe_index_stats()['total_vector_count'])
        for vec in fetch_response.vectors.values():
            if vec.metadata['type'] == 'text':
                self.documents.append(vec.metadata['content'])
        
        # Initialize BM25
        tokenized_docs = [doc.split() for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_docs)
    
    def hybrid_search(self, query, k=5):
        # Semantic search
        query_embedding = self.text_model.encode(query)
        semantic_results = self.index.query(
            vector=query_embedding,
            top_k=k,
            include_metadata=True
        )
        
        # Keyword search
        tokenized_query = query.split()
        keyword_scores = self.bm25.get_scores(tokenized_query)
        top_keyword_indices = np.argsort(keyword_scores)[-k:][::-1]
        
        # Combine results
        combined_results = set()
        for match in semantic_results.matches:
            combined_results.add((match.metadata['content'], match.metadata['type'], match.metadata['page']))
            
        for idx in top_keyword_indices:
            combined_results.add((self.documents[idx], 'text', None))
        
        return list(combined_results)
    
    def query(self, question, k=5):
        results = self.hybrid_search(question, k)
        
        context = ""
        for content, type_, page in results:
            if type_ == 'text':
                context += f"Text: {content}\n"
            else:
                context += f"Image at page {page}: {content}\n"
        
        prompt = PromptTemplate(
            template="""Context information is below. Use it to answer the question.
            Context: {context}
            
            Question: {question}
            
            Answer (include relevant image references if available):""",
            input_variables=["context", "question"]
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run(context=context, question=question)

# Usage
rag = SemanticRAG(
    pinecone_key="YOUR_KEY",
    openai_key="YOUR_KEY", 
    index_name="pdf-store"
)

answer = rag.query("What does the architecture diagram show?")
