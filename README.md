# AI Support Chatbot MVP

A configurable AI-powered support chatbot that ingests data from Zendesk, Jira, and product documentation to provide intelligent customer support responses.

## Features

- **Multi-source Data Ingestion**: Zendesk tickets, Jira tickets, PDF/Word documents
- **Configurable LLM Backend**: Switch between Ollama (local) and OpenAI APIs
- **Version-aware Responses**: Different answers based on product versions
- **Vector Search**: Semantic similarity search with fallback handling
- **REST API**: FastAPI backend with chat endpoints
- **React Widget**: Frontend chat interface with source citations
- **Feedback System**: Thumbs up/down for response quality

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │   Backend API   │    │   Frontend      │
│                 │    │                 │    │                 │
│ • Zendesk       │───▶│ • FastAPI       │◀───│ • React Widget  │
│ • Jira          │    │ • Vector Search │    │ • Chat UI       │
│ • PDF/Word      │    │ • LLM Router    │    │ • Feedback      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Vector DB     │
                       │ • Pinecone      │
                       │ • Weaviate      │
                       └─────────────────┘
```

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **LLM**: Configurable (Ollama local / OpenAI API)
- **Embeddings**: nomic-embed-text (local) / OpenAI embeddings
- **Vector DB**: Pinecone or Weaviate
- **Document Parsing**: PyMuPDF, python-docx, Unstructured

### Frontend
- **Framework**: React
- **UI**: Chat widget component

### Deployment
- **Containerization**: Docker
- **Platform**: Render/AWS/GCP

## Quick Start

### 1. Environment Setup

```bash
# Clone and enter directory
cd ai-support-chatbot

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
```

### 2. Configuration

Copy and configure environment files:

```bash
# Backend configuration
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys and settings

# Frontend configuration  
cp frontend/.env.example frontend/.env
# Edit frontend/.env with backend URL
```

### 3. Local Development (Ollama)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Llama 3.2 model
ollama pull llama3.2

# Start backend (uses local models by default)
cd backend
uvicorn main:app --reload

# Start frontend
cd ../frontend
npm start
```

### 4. Production Setup (OpenAI)

Update backend/.env:
```env
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=your_openai_key
```

## Configuration

### LLM Provider Switching

The system supports easy switching between LLM providers via environment variables:

```env
# Local development with Ollama
LLM_PROVIDER=ollama
EMBEDDING_PROVIDER=local
OLLAMA_MODEL=llama3.2

# Production with OpenAI
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

### Vector Database

Choose between Pinecone (managed) or Weaviate (self-hosted):

```env
# Pinecone (recommended for production)
VECTOR_DB=pinecone
PINECONE_API_KEY=your_key
PINECONE_ENVIRONMENT=your_env

# Weaviate (self-hosted)
VECTOR_DB=weaviate
WEAVIATE_URL=http://localhost:8080
```

## API Documentation

### Chat Endpoint

```http
POST /chat
Content-Type: application/json

{
  "userId": "user123",
  "query": "How do I reset my password?",
  "productVersion": "v3.2"
}
```

Response:
```json
{
  "answer": "To reset your password, go to Settings > Account > Reset Password...",
  "sources": [
    {
      "doc_title": "User Guide v3.2",
      "section": "Account Management",
      "confidence": 0.92
    }
  ],
  "conversation_id": "conv_123"
}
```

### Data Ingestion

```http
POST /ingest/zendesk
POST /ingest/jira  
POST /ingest/documents
```

## Deployment

### Docker

```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Environment Variables

See `.env.example` files for complete configuration options.

## Project Structure

```
ai-support-chatbot/
├── backend/                    # FastAPI backend service
│   ├── app/
│   │   ├── services/          # Core services (LLM, Vector Store, Ingestion)
│   │   ├── models.py          # Pydantic models
│   │   └── config.py          # Configuration management
│   ├── main.py               # FastAPI application entry point
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile           # Backend container configuration
│   └── .env.example         # Environment variables template
├── frontend/                  # React frontend application
│   ├── src/
│   │   ├── components/       # React components (ChatWidget, MessageBubble, etc.)
│   │   ├── api/             # API client and types
│   │   └── App.tsx          # Main application component
│   ├── public/              # Static assets
│   ├── package.json         # Node.js dependencies
│   ├── Dockerfile          # Frontend container configuration
│   └── .env.example        # Frontend environment variables
├── docker-compose.yml       # Multi-service orchestration
├── setup.sh                # Automated setup script
├── configure.sh            # Configuration management script
├── ingest.py               # Data ingestion CLI tool
├── test.py                 # Comprehensive testing script
├── ingestion_config.json   # Sample ingestion configuration
├── DEVELOPMENT.md          # Development documentation
├── DEPLOYMENT.md           # Production deployment guide
└── README.md              # This file
```

## Quick Commands

```bash
# Setup and start all services
./setup.sh

# Configure for production (OpenAI + Pinecone)
./configure.sh set-openai-key sk-your-key-here
./configure.sh switch-llm openai
./configure.sh switch-vectordb pinecone
./configure.sh set-pinecone-key your-pinecone-key

# Ingest sample documents
./ingest.py pdf ./data/documents/manual.pdf --title "User Manual" --product-version "v1.0"

# Test the system
./test.py --quick

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## Development Roadmap

- [x] Core chat functionality with configurable LLM backends
- [x] Vector search and retrieval with similarity thresholding
- [x] Multi-source document ingestion (PDF, DOCX, Zendesk, Jira)
- [x] React chat widget with source citations
- [x] Feedback system with thumbs up/down ratings
- [x] Docker containerization and orchestration
- [x] Comprehensive testing and monitoring
- [x] Production deployment guides
- [ ] Advanced analytics dashboard
- [ ] Multi-tenant support with user isolation
- [ ] Advanced document parsing (tables, images)
- [ ] Conversation memory and context
- [ ] Integration webhooks and APIs
- [ ] Performance optimization and caching

## Customization

The system is designed to be highly configurable:

- **LLM Providers**: Easily switch between Ollama (local) and OpenAI
- **Vector Databases**: Support for Pinecone (managed) and Weaviate (self-hosted)
- **Embedding Models**: Local models via SentenceTransformers or OpenAI embeddings
- **UI Customization**: Themeable React components
- **Data Sources**: Extensible ingestion pipeline for new source types

## Performance

- **Response Time**: < 2 seconds for typical queries
- **Concurrency**: Scales horizontally with stateless backend design
- **Accuracy**: Configurable similarity thresholds with fallback responses
- **Throughput**: Optimized for high-volume customer support scenarios

## Support and Documentation

- **Development Guide**: See [DEVELOPMENT.md](DEVELOPMENT.md)
- **Deployment Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **API Documentation**: Available at `/docs` when backend is running
- **Issues**: Use GitHub issues for bug reports and feature requests

## License

MIT License - see LICENSE file for details.

## Acknowledgments

Built with:
- **FastAPI** for the high-performance backend API
- **React** for the interactive frontend
- **Ollama** for local LLM deployment
- **OpenAI** for production-grade LLM and embeddings
- **Pinecone/Weaviate** for vector storage and search
- **Docker** for containerization and deployment
