import logging
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initializes the embedding service with a specified HuggingFace model.
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)

    def embed_text(self, text: str) -> List[float]:
        """
        Generates an embedding for a single string of text.
        """
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embeddings for a list of documents.
        """
        try:
            return self.embeddings.embed_documents(texts)
        except Exception as e:
            logger.error(f"Error generating embeddings for documents: {e}")
            return []

# Singleton instance
embedding_service = EmbeddingService()
