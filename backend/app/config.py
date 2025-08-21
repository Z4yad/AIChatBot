from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Environment
    environment: str = "development"
    
    # LLM Configuration
    llm_provider: str = "ollama"  # ollama or openai
    embedding_provider: str = "local"  # local or openai
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-large"
    
    # Vector Database
    vector_db: str = "weaviate"  # pinecone or weaviate
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    pinecone_index_name: str = "ai-support-chatbot"
    weaviate_url: str = "http://localhost:8080"
    weaviate_api_key: Optional[str] = None
    
    # Data Sources
    zendesk_subdomain: Optional[str] = None
    zendesk_email: Optional[str] = None
    zendesk_token: Optional[str] = None
    jira_server: Optional[str] = None
    jira_email: Optional[str] = None
    jira_api_token: Optional[str] = None
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    log_level: str = "INFO"
    
    # Retrieval Configuration
    similarity_threshold: float = 0.25
    max_retrieved_chunks: int = 5
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
