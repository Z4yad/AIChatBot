from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import httpx
import openai
from ..config import settings
from ..models import DocumentChunk
import logging

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate_response(
        self, 
        prompt: str, 
        context_chunks: List[DocumentChunk],
        max_tokens: int = 1000
    ) -> str:
        """Generate a response using the LLM."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the LLM provider is healthy."""
        pass


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""
    
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def generate_response(
        self, 
        prompt: str, 
        context_chunks: List[DocumentChunk],
        max_tokens: int = 1000
    ) -> str:
        """Generate response using Ollama."""
        try:
            # Format context from chunks
            context = self._format_context(context_chunks)
            
            # Create the full prompt
            full_prompt = self._create_prompt(prompt, context)
            
            # Call Ollama API
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.1,
                        "top_p": 0.9
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                raise Exception(f"Ollama API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error generating response with Ollama: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check Ollama health."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
    
    def _format_context(self, chunks: List[DocumentChunk]) -> str:
        """Format context chunks for the prompt."""
        if not chunks:
            return "No relevant context found."
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Source {i}] {chunk.metadata.title}\n{chunk.content}\n"
            )
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, query: str, context: str) -> str:
        """Create the full prompt for the LLM."""
        return f"""You are a helpful customer support assistant. Use ONLY the provided context to answer the user's question. 

If the context doesn't contain enough information to answer the question, respond with: "I don't have enough information to answer that question. Please contact our support team for assistance."

Context:
{context}

Question: {query}

Answer:"""


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""
    
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    async def generate_response(
        self, 
        prompt: str, 
        context_chunks: List[DocumentChunk],
        max_tokens: int = 1000
    ) -> str:
        """Generate response using OpenAI."""
        try:
            # Format context from chunks
            context = self._format_context(context_chunks)
            
            # Create messages for chat completion
            messages = [
                {
                    "role": "system",
                    "content": """You are a helpful customer support assistant. Use ONLY the provided context to answer questions. 
                    
If the context doesn't contain enough information, respond with: "I don't have enough information to answer that question. Please contact our support team for assistance."

Be concise, helpful, and cite the relevant sources in your response."""
                },
                {
                    "role": "user", 
                    "content": f"Context:\n{context}\n\nQuestion: {prompt}"
                }
            ]
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.1,
                top_p=0.9
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating response with OpenAI: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check OpenAI health."""
        try:
            # Simple API call to check connectivity
            await self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False
    
    def _format_context(self, chunks: List[DocumentChunk]) -> str:
        """Format context chunks for the prompt."""
        if not chunks:
            return "No relevant context found."
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source_info = f"{chunk.metadata.title}"
            if chunk.metadata.source_type in ["zendesk", "jira"] and "ticket_id" in chunk.metadata.metadata:
                source_info += f" (Ticket #{chunk.metadata.metadata['ticket_id']})"
            
            context_parts.append(f"[Source {i}] {source_info}\n{chunk.content}\n")
        
        return "\n".join(context_parts)


class LLMFactory:
    """Factory for creating LLM providers."""
    
    @staticmethod
    def create_provider() -> LLMProvider:
        """Create LLM provider based on configuration."""
        if settings.llm_provider.lower() == "ollama":
            return OllamaProvider()
        elif settings.llm_provider.lower() == "openai":
            return OpenAIProvider()
        else:
            raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")


# Global LLM provider instance
llm_provider = LLMFactory.create_provider()
