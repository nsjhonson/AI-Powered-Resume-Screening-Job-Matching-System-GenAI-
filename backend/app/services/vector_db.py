import logging
import faiss
import numpy as np
from typing import List, Dict, Tuple
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from .embedding_service import embedding_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorDBService:
    def __init__(self):
        """
        Initializes the Vector DB (FAISS).
        Since FAISS is in-memory by default, this simple implementation will reset on restart.
        For persistence, we would need to save/load the index.
        """
        self.embeddings = embedding_service.embeddings
        
        # Initialize an empty FAISS index
        # We need to know the dimension of the embeddings. all-MiniLM-L6-v2 is 384.
        self.dimension = 384 
        self.index = faiss.IndexFlatL2(self.dimension)
        
        # LangChain FAISS wrapper needs a docstore and index_to_docstore_id
        self.docstore = InMemoryDocstore({})
        self.index_to_docstore_id = {}
        
        self.vector_store = FAISS(
            embedding_function=self.embeddings,
            index=self.index,
            docstore=self.docstore,
            index_to_docstore_id=self.index_to_docstore_id
        )
        logger.info("Vector DB initialized.")

    def add_resume(self, text: str, metadata: Dict):
        """
        Adds a resume to the vector store.
        Metadata should now include the structured data if available.
        """
        try:
            self.vector_store.add_texts(texts=[text], metadatas=[metadata])
            logger.info(f"Added resume for {metadata.get('filename', 'unknown')} to Vector DB.")
        except Exception as e:
            logger.error(f"Error adding resume to Vector DB: {e}")

    def search_similar(self, query: str, k: int = 5) -> List[Tuple[Dict, float]]:
        """
        Searches for similar documents (resumes).
        Returns a list of (metadata, score).
        FAISS returns L2 distance (lower is better), but LangChain wrapper might return similarity.
        Let's use similarity_search_with_score.
        """
        try:
            # results is a list of (Document, score)
            results = self.vector_store.similarity_search_with_score(query, k=k)
            
            # Convert results to a friendlier format
            # Note: FAISS usually returns L2 distance. 
            # We might want to normalize it or just return it as is.
            # Lower score = better match in L2.
            
            formatted_results = []
            for doc, score in results:
                formatted_results.append((doc.metadata, float(score)))
                
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching Vector DB: {e}")
            return []

# Singleton instance
vector_db = VectorDBService()
