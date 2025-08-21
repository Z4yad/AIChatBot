from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import uuid
import logging
import os
import json
import tempfile
import aiofiles
from datetime import datetime

from app.config import settings
from app.models import (
    ChatRequest, ChatResponse, FeedbackRequest, 
    IngestRequest, IngestResponse, HealthResponse,
    Source, DocumentSource, ErrorResponse
)
from app.services.llm import llm_provider
from app.services.vector_store import get_vector_store
from app.services.ingestion import ingestion_service
from app.services.embeddings import embedding_provider

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Support Chatbot API",
    description="Configurable AI-powered support chatbot with multi-source data ingestion",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for conversations and feedback (use Redis/DB in production)
conversations: Dict[str, List[Dict[str, Any]]] = {}
feedback_store: List[Dict[str, Any]] = []


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        logger.info("Initializing AI Support Chatbot API...")
        
        # Initialize vector store
        vector_store = get_vector_store()
        await vector_store.initialize()
        logger.info(f"Vector store initialized: {settings.vector_db}")
        
        # Check LLM provider health
        llm_healthy = await llm_provider.health_check()
        if not llm_healthy:
            logger.warning(f"LLM provider {settings.llm_provider} health check failed")
        
        logger.info("API initialization complete")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Check vector store health
        vector_store = get_vector_store()
        vector_healthy = await vector_store.health_check()
        
        # Check LLM provider health
        llm_healthy = await llm_provider.health_check()
        
        status = "healthy" if vector_healthy and llm_healthy else "degraded"
        
        return HealthResponse(
            status=status,
            version="1.0.0",
            llm_provider=settings.llm_provider,
            embedding_provider=settings.embedding_provider,
            vector_db=settings.vector_db,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint."""
    try:
        # Debug: Log the exact request details
        logger.info(f"FRONTEND REQUEST - user_id: {request.user_id}, query: '{request.query}', product_version: {request.product_version}")
        
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Store conversation message
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        conversations[conversation_id].append({
            "role": "user",
            "content": request.query,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Search for relevant chunks
        filters = {}
        if request.product_version:
            filters["product_version"] = request.product_version
        if request.document_ids:
            filters["document_ids"] = request.document_ids
        
        search_results = await get_vector_store().search(
            query=request.query,
            limit=settings.max_retrieved_chunks,
            filters=filters
        )
        
        # Debug logging
        logger.info(f"Search query: {request.query}")
        logger.info(f"Search results count: {len(search_results)}")
        if search_results:
            logger.info(f"Top result similarity: {search_results[0][1]}")
            logger.info(f"Similarity threshold: {settings.similarity_threshold}")
        
        # Check if we have good enough results
        if not search_results or search_results[0][1] < settings.similarity_threshold:
            # Fallback response
            fallback_answer = "I don't have enough information to answer that question. Please contact our support team for assistance."
            
            conversations[conversation_id].append({
                "role": "assistant",
                "content": fallback_answer,
                "timestamp": datetime.utcnow().isoformat(),
                "fallback": True
            })
            
            return ChatResponse(
                answer=fallback_answer,
                sources=[],
                conversation_id=conversation_id,
                confidence=0.0,
                fallback_triggered=True
            )
        
        # Extract chunks and generate response
        chunks = [result[0] for result in search_results]
        response_text = await llm_provider.generate_response(
            prompt=request.query,
            context_chunks=chunks
        )
        
        # Create source information grouped by document
        source_groups = {}
        for chunk, score in search_results:
            doc_key = f"{chunk.metadata.title}_{chunk.metadata.source_type}"
            
            if doc_key not in source_groups:
                source_groups[doc_key] = {
                    'doc_title': chunk.metadata.title,
                    'source_type': chunk.metadata.source_type,
                    'ticket_id': chunk.metadata.metadata.get("ticket_id"),
                    'scores': [],
                    'chunk_ids': []
                }
            
            source_groups[doc_key]['scores'].append(score)
            source_groups[doc_key]['chunk_ids'].append(chunk.chunk_id)
        
        # Create aggregated sources
        sources = []
        for group_data in source_groups.values():
            # Use the highest confidence score for the document
            max_confidence = max(group_data['scores'])
            # Or use average: avg_confidence = sum(group_data['scores']) / len(group_data['scores'])
            
            source = Source(
                doc_title=group_data['doc_title'],
                section=None,  # Could be enhanced to include section info
                source_type=group_data['source_type'],
                ticket_id=group_data['ticket_id'],
                confidence=max_confidence,
                chunk_id=group_data['chunk_ids'][0]  # Use first chunk ID as representative
            )
            sources.append(source)
        
        # Calculate overall confidence (average of top results)
        overall_confidence = sum(score for _, score in search_results[:3]) / min(3, len(search_results))
        
        # Store assistant response
        conversations[conversation_id].append({
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.utcnow().isoformat(),
            "sources": [source.dict() for source in sources],
            "confidence": overall_confidence
        })
        
        return ChatResponse(
            answer=response_text,
            sources=sources,
            conversation_id=conversation_id,
            confidence=overall_confidence,
            fallback_triggered=False
        )
        
    except Exception as e:
        import traceback
        logger.error(f"Error in chat endpoint: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit feedback for a conversation."""
    try:
        feedback_entry = {
            "feedback_id": str(uuid.uuid4()),
            "conversation_id": request.conversation_id,
            "user_id": request.user_id,
            "rating": request.rating,
            "feedback_text": request.feedback_text,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        feedback_store.append(feedback_entry)
        
        logger.info(f"Feedback received for conversation {request.conversation_id}: {request.rating}/5")
        
        return {"success": True, "feedback_id": feedback_entry["feedback_id"]}
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")


@app.post("/ingest", response_model=IngestResponse)
async def ingest_documents(request: IngestRequest, background_tasks: BackgroundTasks):
    """Ingest documents from various sources."""
    try:
        # For long-running ingestion, we might want to use background tasks
        if request.source_type in [DocumentSource.ZENDESK, DocumentSource.JIRA]:
            task_id = str(uuid.uuid4())
            background_tasks.add_task(
                _background_ingestion,
                task_id,
                request.source_type,
                request.filters
            )
            
            return IngestResponse(
                success=True,
                documents_processed=0,
                chunks_created=0,
                errors=[],
                task_id=task_id
            )
        else:
            # Direct ingestion for files
            chunks = await ingestion_service.ingest_documents(
                source_type=request.source_type,
                filters=request.filters
            )
            
            # Store chunks in vector store
            if chunks:
                await get_vector_store().upsert_chunks(chunks)
            
            return IngestResponse(
                success=True,
                documents_processed=len(set(chunk.doc_id for chunk in chunks)),
                chunks_created=len(chunks),
                errors=[]
            )
            
    except Exception as e:
        logger.error(f"Error in ingestion endpoint: {e}")
        return IngestResponse(
            success=False,
            documents_processed=0,
            chunks_created=0,
            errors=[str(e)]
        )


async def _background_ingestion(task_id: str, source_type: DocumentSource, filters: Dict[str, Any]):
    """Background task for long-running ingestion."""
    try:
        logger.info(f"Starting background ingestion task {task_id} for {source_type}")
        
        chunks = await ingestion_service.ingest_documents(
            source_type=source_type,
            filters=filters
        )
        
        if chunks:
            await get_vector_store().upsert_chunks(chunks)
        
        logger.info(f"Completed background ingestion task {task_id}: {len(chunks)} chunks created")
        
    except Exception as e:
        logger.error(f"Error in background ingestion task {task_id}: {e}")


@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history."""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {
        "conversation_id": conversation_id,
        "messages": conversations[conversation_id]
    }


@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation."""
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"success": True}
    
    raise HTTPException(status_code=404, detail="Conversation not found")


@app.get("/analytics/feedback")
async def get_feedback_analytics():
    """Get feedback analytics."""
    if not feedback_store:
        return {"total_feedback": 0, "average_rating": 0, "rating_distribution": {}}
    
    total_feedback = len(feedback_store)
    average_rating = sum(f["rating"] for f in feedback_store) / total_feedback
    
    rating_distribution = {}
    for rating in range(1, 6):
        count = sum(1 for f in feedback_store if f["rating"] == rating)
        rating_distribution[str(rating)] = count
    
    return {
        "total_feedback": total_feedback,
        "average_rating": round(average_rating, 2),
        "rating_distribution": rating_distribution
    }


@app.post("/upload/file")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    product_version: Optional[str] = Form(None),
    tags: Optional[str] = Form(None)
):
    """Upload and process a document file (DOCX, PDF, TXT, MD)."""
    try:
        # Validate file type
        allowed_extensions = {'.pdf', '.docx', '.txt', '.md'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Create temporary file and stream upload to disk to avoid loading into memory
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file_path = temp_file.name
            # Stream in chunks
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                temp_file.write(chunk)

        # Compute file size from disk for reliability
        file_size = os.path.getsize(temp_file_path)
        
        # Process tags
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        # Prepare filters for ingestion
        filters = {
            "file_path": temp_file_path,
            "title": title or file.filename,
            "product_version": product_version,
            "tags": tag_list
        }
        
        # Determine source type based on extension
        if file_extension == '.pdf':
            source_type = DocumentSource.PDF
        elif file_extension == '.docx':
            source_type = DocumentSource.DOCX
        elif file_extension == '.txt':
            source_type = DocumentSource.TEXT
        elif file_extension == '.md':
            source_type = DocumentSource.MARKDOWN
        else:
            # This shouldn't happen due to validation above, but just in case
            source_type = DocumentSource.TEXT
        
        # Create background task ID
        task_id = str(uuid.uuid4())
        
        # Schedule background ingestion
        background_tasks.add_task(
            _background_file_ingestion,
            task_id,
            source_type,
            filters,
            temp_file_path
        )
        
        logger.info(f"File upload initiated: {file.filename}, task_id: {task_id}")
        
        return {
            "success": True,
            "message": f"File '{file.filename}' uploaded successfully and is being processed",
            "task_id": task_id,
            "file_name": file.filename,
            "file_size": file_size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload/json")
async def upload_json_data(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    data_type: str = Form(...),
    product_version: Optional[str] = Form(None)
):
    """Upload JSON data (helpdesk tickets, zendesk tickets, etc.)."""
    try:
        # Validate file is JSON
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="File must be JSON format")
        
        # Validate data type
        valid_types = ['helpdesk', 'zendesk', 'custom']
        if data_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid data_type. Must be one of: {', '.join(valid_types)}"
            )
        
        # Read and parse JSON
        content = await file.read()
        try:
            json_data = json.loads(content)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")
        
        # Validate JSON structure
        if not isinstance(json_data, list):
            raise HTTPException(status_code=400, detail="JSON must be an array of objects")
        
        # Create task ID
        task_id = str(uuid.uuid4())
        
        # Schedule background processing
        background_tasks.add_task(
            _background_json_ingestion,
            task_id,
            json_data,
            data_type,
            product_version
        )
        
        logger.info(f"JSON data upload initiated: {file.filename}, type: {data_type}, task_id: {task_id}")
        
        return {
            "success": True,
            "message": f"JSON data uploaded successfully and is being processed",
            "task_id": task_id,
            "data_type": data_type,
            "records_count": len(json_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading JSON data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/upload/status/{task_id}")
async def get_upload_status(task_id: str):
    """Get the status of an upload task."""
    # In a real implementation, you'd check the task status from a job queue
    # For now, return a simple response
    return {
        "task_id": task_id,
        "status": "completed",
        "message": "Upload processing completed successfully"
    }


async def _background_file_ingestion(
    task_id: str,
    source_type: DocumentSource,
    filters: Dict[str, Any],
    temp_file_path: str
):
    """Background task for file ingestion."""
    try:
        logger.info(f"Starting background file ingestion task {task_id}")
        
        # Process the file
        chunks = await ingestion_service.ingest_documents(
            source_type=source_type,
            filters=filters
        )
        
        if chunks:
            await get_vector_store().upsert_chunks(chunks)
        
        logger.info(f"Completed background file ingestion task {task_id}: {len(chunks)} chunks created")
        
    except Exception as e:
        logger.error(f"Error in background file ingestion task {task_id}: {e}")
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
        except Exception as e:
            logger.warning(f"Failed to delete temporary file {temp_file_path}: {e}")


async def _background_json_ingestion(
    task_id: str,
    json_data: List[Dict[str, Any]],
    data_type: str,
    product_version: Optional[str]
):
    """Background task for JSON data ingestion."""
    try:
        logger.info(f"Starting background JSON ingestion task {task_id}")
        
        chunks = []
        for item in json_data:
            # Convert JSON items to document chunks
            chunk_content = _json_to_text(item, data_type)
            
            # Create chunk metadata
            from app.models import DocumentChunk, DocumentMetadata
            
            if data_type == 'helpdesk':
                doc_id = f"helpdesk_{item.get('id', str(uuid.uuid4()))}"
                title = item.get('title', 'Helpdesk Ticket')
                source_type = DocumentSource.ZENDESK  # Using ZENDESK for helpdesk
            elif data_type == 'zendesk':
                doc_id = f"zendesk_{item.get('id', str(uuid.uuid4()))}"
                title = item.get('subject', 'Zendesk Ticket')
                source_type = DocumentSource.ZENDESK
            else:
                doc_id = f"custom_{str(uuid.uuid4())}"
                title = item.get('title') or item.get('name') or 'Custom Document'
                source_type = DocumentSource.DOCX
            
            metadata = DocumentMetadata(
                doc_id=doc_id,
                title=title,
                source_type=source_type,
                product_version=product_version,
                tags=item.get('tags', []),
                metadata={"source": "json_upload", "data_type": data_type}
            )
            
            chunk = DocumentChunk(
                chunk_id=str(uuid.uuid4()),
                doc_id=doc_id,
                content=chunk_content,
                metadata=metadata,
                chunk_index=0
            )
            chunks.append(chunk)
        
        if chunks:
            await get_vector_store().upsert_chunks(chunks)
        
        logger.info(f"Completed background JSON ingestion task {task_id}: {len(chunks)} chunks created")
        
    except Exception as e:
        logger.error(f"Error in background JSON ingestion task {task_id}: {e}")


def _json_to_text(item: Dict[str, Any], data_type: str) -> str:
    """Convert JSON item to searchable text content."""
    if data_type == 'helpdesk':
        return f"""
        Ticket ID: {item.get('id', 'N/A')}
        Title: {item.get('title', 'N/A')}
        Description: {item.get('description', 'N/A')}
        Category: {item.get('category', 'N/A')}
        Priority: {item.get('priority', 'N/A')}
        Status: {item.get('status', 'N/A')}
        Resolution: {item.get('resolution', 'N/A')}
        Tags: {', '.join(item.get('tags', []))}
        """
    elif data_type == 'zendesk':
        text = f"""
        Ticket ID: {item.get('id', 'N/A')}
        Subject: {item.get('subject', 'N/A')}
        Description: {item.get('description', 'N/A')}
        Priority: {item.get('priority', 'N/A')}
        Status: {item.get('status', 'N/A')}
        Tags: {', '.join(item.get('tags', []))}
        """
        
        # Add comments if available
        comments = item.get('comments', [])
        if comments:
            text += "\nComments:\n"
            for comment in comments:
                text += f"- {comment.get('body', 'N/A')}\n"
        
        return text
    else:
        # For custom data, try to extract common fields
        text_parts = []
        for key, value in item.items():
            if isinstance(value, (str, int, float)):
                text_parts.append(f"{key}: {value}")
            elif isinstance(value, list):
                text_parts.append(f"{key}: {', '.join(map(str, value))}")
        
        return '\n'.join(text_parts)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return ErrorResponse(
        error="Internal server error",
        detail=str(exc) if settings.environment == "development" else "An unexpected error occurred",
        code="INTERNAL_ERROR",
        timestamp=datetime.utcnow()
    )


@app.get("/documents")
async def get_documents():
    """Get all documents in the knowledge base."""
    try:
        vector_store = get_vector_store()
        documents = await vector_store.get_all_documents()
        return {"documents": documents}
    except Exception as e:
        logger.error(f"Error fetching documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch documents")


@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from the knowledge base."""
    try:
        vector_store = get_vector_store()
        success = await vector_store.delete_document(document_id)
        if success:
            return {"message": f"Document {document_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development"
    )
