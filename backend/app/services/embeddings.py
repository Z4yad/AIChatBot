from abc import ABC, abstractmethod
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import openai
from ..config import settings
import logging

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""
    
    @abstractmethod
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        pass
    
    @abstractmethod
    async def generate_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Get the dimension of the embeddings."""
        pass


class LocalEmbeddingProvider(EmbeddingProvider):
    """Local embedding provider using SentenceTransformers."""
    
    def __init__(self):
        # Using a more compatible model that doesn't require trust_remote_code
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384  # all-MiniLM-L6-v2 dimension
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        try:
            # SentenceTransformer.encode is synchronous, but we can make it async-friendly
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    async def generate_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            embedding = self.model.encode([text], convert_to_numpy=True)
            return embedding[0].tolist()
        except Exception as e:
            logger.error(f"Error generating single embedding: {e}")
            raise
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embedding provider."""
    
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_embedding_model
        self.dimension = 3072 if "3-large" in self.model else 1536  # text-embedding-3-large vs others
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API."""
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            
            return [data.embedding for data in response.data]
            
        except Exception as e:
            logger.error(f"Error generating embeddings with OpenAI: {e}")
            raise
    
    async def generate_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=[text]
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error generating single embedding with OpenAI: {e}")
            raise
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension


class EmbeddingFactory:
    """Factory for creating embedding providers."""
    
    @staticmethod
    def create_provider() -> EmbeddingProvider:
        """Create embedding provider based on configuration."""
        if settings.embedding_provider.lower() == "local":
            return LocalEmbeddingProvider()
        elif settings.embedding_provider.lower() == "openai":
            return OpenAIEmbeddingProvider()
        else:
            raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")


# Global embedding provider instance
embedding_provider = EmbeddingFactory.create_provider()
