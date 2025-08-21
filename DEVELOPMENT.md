# Development Documentation

## Quick Start Guide

### 1. Initial Setup

```bash
# Clone and enter the project directory
cd ai-support-chatbot

# Run the setup script
./setup.sh
```

This will:
- Create environment files from templates
- Start all services with Docker Compose
- Pull the Llama 3.2 model for Ollama
- Check service health

### 2. Configuration

#### Switch to OpenAI (Recommended for Production)

```bash
# Set OpenAI API key
./configure.sh set-openai-key sk-your-openai-key-here

# Switch to OpenAI for LLM
./configure.sh switch-llm openai

# Switch to OpenAI for embeddings
./configure.sh switch-embeddings openai

# Restart backend to apply changes
docker-compose restart backend
```

#### Use Pinecone (Recommended for Production)

```bash
# Set Pinecone credentials
./configure.sh set-pinecone-key your-pinecone-key-here
# Edit backend/.env to set PINECONE_ENVIRONMENT

# Switch to Pinecone
./configure.sh switch-vectordb pinecone

# Restart backend
docker-compose restart backend
```

### 3. Data Ingestion

#### Ingest PDF Documents

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "pdf",
    "filters": {
      "file_path": "/path/to/your/document.pdf",
      "title": "User Manual v1.0",
      "product_version": "v1.0"
    }
  }'
```

#### Ingest Zendesk Tickets

First, configure Zendesk credentials in `backend/.env`:
```bash
ZENDESK_SUBDOMAIN=your-company
ZENDESK_EMAIL=your-email@company.com
ZENDESK_TOKEN=your-zendesk-token
```

Then ingest:
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "zendesk",
    "filters": {
      "limit": 100,
      "product_version": "v1.0"
    }
  }'
```

#### Ingest Jira Issues

Configure Jira credentials in `backend/.env`:
```bash
JIRA_SERVER=https://your-company.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-jira-token
```

Then ingest:
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "jira",
    "filters": {
      "jql": "project = SUPPORT",
      "limit": 100,
      "product_version": "v1.0"
    }
  }'
```

### 4. Testing the Chat

#### Via Frontend
1. Open http://localhost:3000
2. Type a question in the chat widget
3. Review the response and sources

#### Via API
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "query": "How do I reset my password?",
    "product_version": "v1.0"
  }'
```

### 5. Monitoring and Debugging

#### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f ollama
```

#### Check Service Health
```bash
# Backend health
curl http://localhost:8000/health

# Current configuration
./configure.sh show-config

# Validate configuration
./configure.sh validate
```

#### Access Service UIs
- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Weaviate Console**: http://localhost:8080/console

## Development Workflow

### Backend Development

1. **Edit Code**: Make changes to Python files in `backend/`
2. **Hot Reload**: The development server automatically reloads
3. **View Logs**: `docker-compose logs -f backend`
4. **Test Changes**: Use the API documentation at http://localhost:8000/docs

### Frontend Development

1. **Edit Code**: Make changes to React files in `frontend/src/`
2. **Hot Reload**: React development server automatically reloads
3. **View Logs**: `docker-compose logs -f frontend`
4. **Test Changes**: View at http://localhost:3000

### Adding New Features

#### New LLM Provider

1. Create a new provider class in `backend/app/services/llm.py`
2. Implement the `LLMProvider` interface
3. Add the provider to `LLMFactory.create_provider()`
4. Update configuration options

#### New Data Source

1. Create a new ingester class in `backend/app/services/ingestion.py`
2. Implement the `DataIngester` interface
3. Add the ingester to `IngestionService.__init__()`
4. Update the `DocumentSource` enum

#### New Vector Store

1. Create a new store class in `backend/app/services/vector_store.py`
2. Implement the `VectorStore` interface
3. Add the store to `VectorStoreFactory.create_store()`
4. Update configuration options

## Production Deployment

### Environment Variables

For production deployment, ensure these environment variables are set:

```bash
# Backend
ENVIRONMENT=production
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=openai
VECTOR_DB=pinecone
OPENAI_API_KEY=your-openai-key
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=your-pinecone-env
SECRET_KEY=your-secret-key

# Frontend
REACT_APP_API_BASE_URL=https://your-api-domain.com
```

### Docker Production Build

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Health Checks

The system includes health check endpoints:
- Backend: `/health`
- Individual component health checks in the health response

### Scaling

- **Backend**: Horizontally scalable (stateless)
- **Vector DB**: Use managed services (Pinecone) for auto-scaling
- **LLM**: Use OpenAI API for managed scaling

## Troubleshooting

### Common Issues

1. **Ollama Model Not Found**
   ```bash
   docker-compose exec ollama ollama pull llama3.2
   ```

2. **Backend Import Errors**
   ```bash
   docker-compose exec backend pip install -r requirements.txt
   ```

3. **Frontend Build Errors**
   ```bash
   docker-compose exec frontend npm install
   ```

4. **Vector Store Connection Issues**
   - Check service logs
   - Verify credentials
   - Ensure services are running

5. **Low Quality Responses**
   - Check similarity threshold in configuration
   - Review ingested data quality
   - Verify embedding model performance

### Performance Optimization

1. **Similarity Threshold**: Adjust `SIMILARITY_THRESHOLD` in backend/.env
2. **Chunk Size**: Optimize `CHUNK_SIZE` for your documents
3. **Retrieved Chunks**: Tune `MAX_RETRIEVED_CHUNKS` for context vs speed
4. **Embedding Caching**: Implement Redis caching for production

### Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **CORS**: Configure appropriate CORS origins for production
3. **Authentication**: Implement user authentication for production use
4. **Rate Limiting**: Add rate limiting to prevent abuse
5. **Input Validation**: Validate all user inputs
