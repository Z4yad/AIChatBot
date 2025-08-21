from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
import pinecone
import weaviate
import uuid
import json
from ..config import settings
from ..models import DocumentChunk, Source
from .embeddings import embedding_provider
import logging

logger = logging.getLogger(__name__)


class VectorStore(ABC):
    """Abstract base class for vector stores."""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the vector store."""
        pass
    
    @abstractmethod
    async def upsert_chunks(self, chunks: List[DocumentChunk]) -> None:
        """Upsert document chunks to the vector store."""
        pass
    
    @abstractmethod
    async def search(
        self, 
        query: str, 
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[DocumentChunk, float]]:
        """Search for similar chunks."""
        pass
    
    @abstractmethod
    async def delete_by_doc_id(self, doc_id: str) -> None:
        """Delete all chunks for a document."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check vector store health."""
        pass
    
    @abstractmethod
    async def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents in the knowledge base."""
        pass
    
    @abstractmethod
    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document and all its chunks."""
        pass


class PineconeStore(VectorStore):
    """Pinecone vector store implementation."""
    
    def __init__(self):
        if not settings.pinecone_api_key:
            raise ValueError("Pinecone API key is required")
        
        pinecone.init(
            api_key=settings.pinecone_api_key,
            environment=settings.pinecone_environment
        )
        
        self.index_name = settings.pinecone_index_name
        self.index = None
    
    async def initialize(self) -> None:
        """Initialize Pinecone index."""
        try:
            # Check if index exists
            existing_indexes = pinecone.list_indexes()
            
            if self.index_name not in existing_indexes:
                # Create index
                pinecone.create_index(
                    name=self.index_name,
                    dimension=embedding_provider.get_dimension(),
                    metric="cosine"
                )
                logger.info(f"Created Pinecone index: {self.index_name}")
            
            self.index = pinecone.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Error initializing Pinecone: {e}")
            raise
    
    async def upsert_chunks(self, chunks: List[DocumentChunk]) -> None:
        """Upsert chunks to Pinecone."""
        try:
            vectors = []
            
            for chunk in chunks:
                # Generate embedding if not present
                if not chunk.embedding:
                    chunk.embedding = await embedding_provider.generate_single_embedding(chunk.content)
                
                # Prepare metadata
                metadata = {
                    "doc_id": chunk.doc_id,
                    "content": chunk.content,
                    "title": chunk.metadata.title,
                    "source_type": chunk.metadata.source_type.value,
                    "chunk_index": chunk.chunk_index,
                    "created_at": chunk.metadata.created_at.isoformat(),
                }
                
                # Add optional fields
                if chunk.metadata.product_version:
                    metadata["product_version"] = chunk.metadata.product_version
                
                if chunk.metadata.tags:
                    metadata["tags"] = ",".join(chunk.metadata.tags)
                
                # Add custom metadata
                metadata.update(chunk.metadata.metadata)
                
                vectors.append({
                    "id": chunk.chunk_id,
                    "values": chunk.embedding,
                    "metadata": metadata
                })
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
            
            logger.info(f"Upserted {len(chunks)} chunks to Pinecone")
            
        except Exception as e:
            logger.error(f"Error upserting to Pinecone: {e}")
            raise
    
    async def search(
        self, 
        query: str, 
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[DocumentChunk, float]]:
        """Search Pinecone for similar chunks."""
        try:
            # Generate query embedding
            query_embedding = await embedding_provider.generate_single_embedding(query)
            
            # Prepare filters
            pinecone_filter = {}
            if filters:
                if "product_version" in filters:
                    pinecone_filter["product_version"] = {"$eq": filters["product_version"]}
                if "source_type" in filters:
                    pinecone_filter["source_type"] = {"$eq": filters["source_type"]}
            
            # Search
            results = self.index.query(
                vector=query_embedding,
                top_k=limit,
                include_metadata=True,
                filter=pinecone_filter if pinecone_filter else None
            )
            
            # Convert results to DocumentChunk objects
            chunks_with_scores = []
            for match in results.matches:
                metadata = match.metadata
                
                # Reconstruct DocumentChunk
                from ..models import DocumentMetadata, DocumentSource
                from datetime import datetime
                
                doc_metadata = DocumentMetadata(
                    doc_id=metadata["doc_id"],
                    title=metadata["title"],
                    source_type=DocumentSource(metadata["source_type"]),
                    product_version=metadata.get("product_version"),
                    created_at=datetime.fromisoformat(metadata["created_at"]),
                    tags=metadata.get("tags", "").split(",") if metadata.get("tags") else [],
                    metadata={k: v for k, v in metadata.items() 
                             if k not in ["doc_id", "content", "title", "source_type", 
                                        "chunk_index", "created_at", "product_version", "tags"]}
                )
                
                chunk = DocumentChunk(
                    chunk_id=match.id,
                    doc_id=metadata["doc_id"],
                    content=metadata["content"],
                    metadata=doc_metadata,
                    chunk_index=metadata["chunk_index"]
                )
                
                chunks_with_scores.append((chunk, match.score))
            
            return chunks_with_scores
            
        except Exception as e:
            logger.error(f"Error searching Pinecone: {e}")
            raise
    
    async def delete_by_doc_id(self, doc_id: str) -> None:
        """Delete chunks by document ID."""
        try:
            # Query to get all chunk IDs for the document
            results = self.index.query(
                vector=[0] * embedding_provider.get_dimension(),  # Dummy vector
                top_k=10000,  # Large number to get all chunks
                include_metadata=True,
                filter={"doc_id": {"$eq": doc_id}}
            )
            
            # Delete chunks
            chunk_ids = [match.id for match in results.matches]
            if chunk_ids:
                self.index.delete(ids=chunk_ids)
                logger.info(f"Deleted {len(chunk_ids)} chunks for doc_id: {doc_id}")
            
        except Exception as e:
            logger.error(f"Error deleting from Pinecone: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check Pinecone health."""
        try:
            stats = self.index.describe_index_stats()
            return True
        except Exception as e:
            logger.error(f"Pinecone health check failed: {e}")
            return False
    
    async def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents in the knowledge base."""
        try:
            # This is a simple implementation - could be optimized
            return []  # Pinecone doesn't easily support document listing
        except Exception as e:
            logger.error(f"Error getting documents from Pinecone: {e}")
            raise
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document and all its chunks."""
        try:
            await self.delete_by_doc_id(doc_id)
            return True
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False


class WeaviateStore(VectorStore):
    """Weaviate vector store implementation."""
    
    def __init__(self):
        # Only use authentication if we have a real API key
        if settings.weaviate_api_key and settings.weaviate_api_key.strip() and settings.weaviate_api_key != "optional_weaviate_api_key":
            self.client = weaviate.Client(
                url=settings.weaviate_url,
                auth_client_secret=weaviate.AuthApiKey(api_key=settings.weaviate_api_key)
            )
        else:
            self.client = weaviate.Client(url=settings.weaviate_url)
        self.class_name = "DocumentChunk"
    
    async def initialize(self) -> None:
        """Initialize Weaviate schema."""
        try:
            # Check if class exists
            schema = self.client.schema.get()
            class_exists = any(cls["class"] == self.class_name for cls in schema.get("classes", []))
            
            if not class_exists:
                # Create class schema
                class_schema = {
                    "class": self.class_name,
                    "description": "Document chunks for AI support chatbot",
                    "vectorizer": "none",  # We provide our own vectors
                    "properties": [
                        {"name": "doc_id", "dataType": ["string"]},
                        {"name": "content", "dataType": ["text"]},
                        {"name": "title", "dataType": ["string"]},
                        {"name": "source_type", "dataType": ["string"]},
                        {"name": "chunk_index", "dataType": ["int"]},
                        {"name": "product_version", "dataType": ["string"]},
                        {"name": "created_at", "dataType": ["date"]},
                        {"name": "tags", "dataType": ["string[]"]},
                        {"name": "metadata", "dataType": ["text"]},  # Store metadata as JSON string
                    ]
                }
                
                self.client.schema.create_class(class_schema)
                logger.info(f"Created Weaviate class: {self.class_name}")
            
            logger.info("Weaviate initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Weaviate: {e}")
            raise
    
    async def upsert_chunks(self, chunks: List[DocumentChunk]) -> None:
        """Upsert chunks to Weaviate."""
        try:
            with self.client.batch as batch:
                for chunk in chunks:
                    # Generate embedding if not present
                    if not chunk.embedding:
                        chunk.embedding = await embedding_provider.generate_single_embedding(chunk.content)
                    
                    # Prepare data object
                    data_object = {
                        "doc_id": chunk.doc_id,
                        "content": chunk.content,
                        "title": chunk.metadata.title,
                        "source_type": chunk.metadata.source_type.value,
                        "chunk_index": chunk.chunk_index,
                        "product_version": chunk.metadata.product_version,
                        "created_at": chunk.metadata.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                        "tags": chunk.metadata.tags,
                        "metadata": json.dumps(chunk.metadata.metadata) if chunk.metadata.metadata else "{}",
                    }
                    
                    batch.add_data_object(
                        data_object=data_object,
                        class_name=self.class_name,
                        uuid=chunk.chunk_id,
                        vector=chunk.embedding
                    )
            
            logger.info(f"Upserted {len(chunks)} chunks to Weaviate")
            
        except Exception as e:
            logger.error(f"Error upserting to Weaviate: {e}")
            raise
    
    async def search(
        self, 
        query: str, 
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[DocumentChunk, float]]:
        """Search Weaviate for similar chunks."""
        try:
            # Generate query embedding
            query_embedding = await embedding_provider.generate_single_embedding(query)
            
            # Build query
            query_builder = (
                self.client.query
                .get(self.class_name, [
                    "doc_id", "content", "title", "source_type", 
                    "chunk_index", "product_version", "created_at", "tags", "metadata"
                ])
                .with_near_vector({"vector": query_embedding})
                .with_limit(limit)
                .with_additional(["distance", "id"])
            )
            
            # Add filters
            if filters:
                where_filter = {"operator": "And", "operands": []}
                
                if "product_version" in filters:
                    where_filter["operands"].append({
                        "path": ["product_version"],
                        "operator": "Equal",
                        "valueString": filters["product_version"]
                    })
                
                if "source_type" in filters:
                    where_filter["operands"].append({
                        "path": ["source_type"],
                        "operator": "Equal",
                        "valueString": filters["source_type"]
                    })
                
                if "document_ids" in filters and filters["document_ids"]:
                    doc_filter = {
                        "operator": "Or",
                        "operands": [
                            {
                                "path": ["doc_id"],
                                "operator": "Equal", 
                                "valueString": doc_id
                            } for doc_id in filters["document_ids"]
                        ]
                    }
                    where_filter["operands"].append(doc_filter)
                
                if where_filter["operands"]:
                    query_builder = query_builder.with_where(where_filter)
            
            # Execute query
            results = query_builder.do()
            
            # Convert results to DocumentChunk objects
            chunks_with_scores = []
            for item in results["data"]["Get"][self.class_name]:
                from ..models import DocumentMetadata, DocumentSource
                from datetime import datetime
                import json
                
                doc_metadata = DocumentMetadata(
                    doc_id=item["doc_id"],
                    title=item["title"],
                    source_type=DocumentSource(item["source_type"]),
                    product_version=item.get("product_version"),
                    created_at=datetime.fromisoformat(item["created_at"]),
                    tags=item.get("tags", []),
                    metadata=json.loads(item.get("metadata", "{}")) if isinstance(item.get("metadata"), str) else item.get("metadata", {})
                )
                
                chunk = DocumentChunk(
                    chunk_id=item["_additional"]["id"],
                    doc_id=item["doc_id"],
                    content=item["content"],
                    metadata=doc_metadata,
                    chunk_index=item["chunk_index"]
                )
                
                # Convert distance to similarity score (lower distance = higher similarity)
                similarity = 1 - item["_additional"]["distance"]
                chunks_with_scores.append((chunk, similarity))
            
            return chunks_with_scores
            
        except Exception as e:
            logger.error(f"Error searching Weaviate: {e}")
            raise
    
    async def delete_by_doc_id(self, doc_id: str) -> None:
        """Delete chunks by document ID."""
        try:
            where_filter = {
                "path": ["doc_id"],
                "operator": "Equal",
                "valueString": doc_id
            }
            
            result = self.client.batch.delete_objects(
                class_name=self.class_name,
                where=where_filter
            )
            
            logger.info(f"Deleted chunks for doc_id: {doc_id}")
            
        except Exception as e:
            logger.error(f"Error deleting from Weaviate: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check Weaviate health."""
        try:
            self.client.cluster.get_nodes_status()
            return True
        except Exception as e:
            logger.error(f"Weaviate health check failed: {e}")
            return False
    
    async def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents in the knowledge base."""
        try:
            # Group chunks by document
            result = self.client.query.get(
                self.class_name,
                ["title", "doc_id", "source_type", "created_at", "product_version"]
            ).with_additional(["id"]).with_limit(10000).do()
            
            documents = {}
            for item in result.get("data", {}).get("Get", {}).get(self.class_name, []):
                doc_id = item.get("doc_id")
                if doc_id not in documents:
                    documents[doc_id] = {
                        "id": doc_id,
                        "title": item.get("title", ""),
                        "source_type": item.get("source_type", ""),
                        "created_at": item.get("created_at", ""),
                        "product_version": item.get("product_version"),
                        "chunks_count": 0
                    }
                documents[doc_id]["chunks_count"] += 1
            
            return list(documents.values())
            
        except Exception as e:
            logger.error(f"Error getting documents from Weaviate: {e}")
            raise
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document and all its chunks."""
        try:
            await self.delete_by_doc_id(doc_id)
            return True
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False


class VectorStoreFactory:
    """Factory for creating vector stores."""
    
    @staticmethod
    def create_store() -> VectorStore:
        """Create vector store based on configuration."""
        if settings.vector_db.lower() == "pinecone":
            return PineconeStore()
        elif settings.vector_db.lower() == "weaviate":
            return WeaviateStore()
        else:
            raise ValueError(f"Unsupported vector store: {settings.vector_db}")


# Global vector store instance (lazy initialization)
_vector_store = None

def get_vector_store() -> VectorStore:
    """Get the global vector store instance (lazy initialization)."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStoreFactory.create_store()
    return _vector_store

# For backward compatibility
vector_store = None  # Will be set on first access
