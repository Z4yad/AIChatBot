from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentSource(str, Enum):
    """Supported document sources."""
    ZENDESK = "zendesk"
    JIRA = "jira"
    PDF = "pdf"
    DOCX = "docx"
    TEXT = "txt"
    MARKDOWN = "md"


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    user_id: str = Field(..., description="Unique identifier for the user")
    query: str = Field(..., min_length=1, description="User's question or query")
    product_version: Optional[str] = Field(None, description="Product version for filtering")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    document_ids: Optional[List[str]] = Field(None, description="Specific document IDs to search within")


class Source(BaseModel):
    """Source information for retrieved content."""
    doc_title: str = Field(..., description="Title of the source document")
    section: Optional[str] = Field(None, description="Section within the document")
    source_type: DocumentSource = Field(..., description="Type of source")
    ticket_id: Optional[str] = Field(None, description="Ticket ID for Zendesk/Jira")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Similarity confidence score")
    chunk_id: str = Field(..., description="Unique identifier for the chunk")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    answer: str = Field(..., description="Generated answer from the LLM")
    sources: List[Source] = Field(default_factory=list, description="Source documents used")
    conversation_id: str = Field(..., description="Conversation ID")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence in the answer")
    fallback_triggered: bool = Field(default=False, description="Whether fallback response was used")


class FeedbackRequest(BaseModel):
    """Request model for feedback endpoint."""
    conversation_id: str = Field(..., description="Conversation ID")
    user_id: str = Field(..., description="User providing feedback")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    feedback_text: Optional[str] = Field(None, description="Optional feedback text")


class DocumentMetadata(BaseModel):
    """Metadata for indexed documents."""
    doc_id: str = Field(..., description="Unique document identifier")
    title: str = Field(..., description="Document title")
    source_type: DocumentSource = Field(..., description="Type of source")
    product_version: Optional[str] = Field(None, description="Product version")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list, description="Document tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class DocumentChunk(BaseModel):
    """Document chunk for vector storage."""
    chunk_id: str = Field(..., description="Unique chunk identifier")
    doc_id: str = Field(..., description="Parent document ID")
    content: str = Field(..., description="Chunk content")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding")
    metadata: DocumentMetadata = Field(..., description="Document metadata")
    chunk_index: int = Field(..., description="Chunk position in document")


class IngestRequest(BaseModel):
    """Request model for document ingestion."""
    source_type: DocumentSource = Field(..., description="Type of source to ingest")
    product_version: Optional[str] = Field(None, description="Product version")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Source-specific filters")


class IngestResponse(BaseModel):
    """Response model for document ingestion."""
    success: bool = Field(..., description="Whether ingestion was successful")
    documents_processed: int = Field(..., description="Number of documents processed")
    chunks_created: int = Field(..., description="Number of chunks created")
    errors: List[str] = Field(default_factory=list, description="List of errors encountered")
    task_id: Optional[str] = Field(None, description="Background task ID if applicable")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    llm_provider: str = Field(..., description="Current LLM provider")
    embedding_provider: str = Field(..., description="Current embedding provider")
    vector_db: str = Field(..., description="Current vector database")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
