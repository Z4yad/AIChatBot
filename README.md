# 🤖 AI Support Chatbot

A beautiful, modern AI-powered support chatbot with **NotebookLM-inspired UI** that provides intelligent responses using your uploaded documents as context.

![AI Support Chatbot](https://img.shields.io/badge/AI-Support%20Chatbot-blue?style=for-the-badge)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=for-the-badge&logo=typescript)

## ✨ Features

### 🎨 **NotebookLM-Inspired Design**
- **Authentic Google design language** with professional dark theme
- **Google Sans typography** throughout the interface  
- **Signature color palette** (#8ab4f8, #34a853, #fbbc04, #ea4335)
- **Advanced glassmorphism** with 40px backdrop blur and enhanced saturation
- **Smooth animations** using Google's cubic-bezier timing functions

### 📁 **Smart Document Management**
- **Upload multiple file types**: PDF, Word (.docx), Text (.txt), Markdown (.md)
- **Intelligent document grouping**: No duplicate chunks, clean unified view
- **Source filtering**: Select specific documents for targeted responses
- **Real-time management**: Add, view, and delete documents instantly

### 💬 **Advanced AI Chat**
- **Context-aware responses** using your uploaded documents
- **Grouped confidence results** by original document (no chunk duplication)
- **Source citations** with confidence scores
- **Fallback handling** for queries outside document scope
- **Conversation memory** within sessions

### 🔧 **Technical Excellence**
- **Vector similarity search** with Weaviate database
- **Semantic document chunking** for optimal retrieval
- **Local LLM processing** with Ollama (Llama 3.1)
- **Containerized architecture** for easy deployment
- **Production-ready** with health checks and monitoring

## 🏗️ Architecture

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐    ┌──────────────────┐
│   Frontend (React)  │    │  Backend (FastAPI)   │    │  Vector DB (Weaviate) │    │  LLM (Ollama)    │
│                     │    │                      │    │                     │    │                  │
│ ✨ NotebookLM UI    │◄──►│ 🚀 Smart APIs       │◄──►│ 🧠 Vector Storage   │◄──►│ 🤖 Llama 3.1    │
│ 📁 Document Groups  │    │ 📊 Source Grouping   │    │ 🔍 Semantic Search  │    │ 💭 Local LLM     │
│ 💬 Chat Interface   │    │ 📤 File Processing   │    │ 📈 Similarity Rank  │    │ 🔒 Privacy First │
│ 📖 Source Citations │    │ 🎯 Confidence Scores │    │ ⚡ Fast Retrieval   │    │                  │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘    └──────────────────┘
```

### **Key Design Principles**
- 🎨 **NotebookLM aesthetic** for professional, Google-like experience
- 📚 **Document-first approach** with intelligent grouping and source management
- 🔗 **Seamless integration** between all components for smooth user experience
- 🛡️ **Privacy-focused** with local LLM processing and no external data sharing

## 🛠️ Tech Stack

### **Frontend**
- **React 18** with TypeScript for type safety
- **Google Sans** typography for authentic NotebookLM feel
- **Advanced CSS** with glassmorphism and backdrop filters
- **Responsive design** optimized for chat interfaces

### **Backend**  
- **FastAPI** for high-performance async APIs
- **Weaviate** vector database for semantic search
- **Ollama** for local LLM processing (Llama 3.1)
- **Python** document processing with chunking algorithms

### **DevOps**
- **Docker Compose** for easy development setup
- **Pydantic** for robust data validation
- **Uvicorn** ASGI server for production deployment
- **CORS** configured for secure cross-origin requests

### Deployment
- **Containerization**: Docker
- **Platform**: Render/AWS/GCP

## 🚀 Quick Start

### **Prerequisites**
- Docker and Docker Compose
- Node.js 16+ (for frontend development)
- Python 3.9+ (for backend development)

### **1. Clone the Repository**
```bash
git clone https://github.com/Z4yad/AIChatBot.git
cd AIChatBot
```

### **2. Start All Services**
```bash
# Launch the complete stack
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### **3. Access Your AI Chatbot**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### **4. Upload Documents & Start Chatting**
1. Upload your PDF, Word, or text documents
2. Wait for processing and indexing
3. Start asking questions about your content
4. Enjoy the NotebookLM-inspired experience!

## ⚙️ Development Setup

### **For Advanced Development**

If you want to run components separately for development:

#### **Backend Development**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### **Frontend Development**  
```bash
cd frontend
npm install
npm start
```

#### **Install Ollama (for local LLM)**
```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the model
ollama pull llama3.1

# Verify installation
ollama list
```

## 🔧 Configuration

### **Environment Variables**
Create `.env` files in backend directory:

```env
# LLM Configuration
LLM_PROVIDER=ollama
EMBEDDING_PROVIDER=local
OLLAMA_MODEL=llama3.1

# Vector Database
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=optional

# API Settings  
CORS_ORIGINS=http://localhost:3000
DEBUG=true
```

## 📚 API Documentation

### **Chat Endpoint**
```http
POST /chat
Content-Type: application/json

{
  "user_id": "user123",
  "query": "How do I use this feature?",
  "document_ids": ["doc1", "doc2"]
}
```

**Response:**
```json
{
  "answer": "Based on your documents...",
  "sources": [
    {
      "document_title": "User Guide.pdf",
      "confidence": 0.95,
      "content": "Relevant excerpt..."
    }
  ],
  "conversation_id": "conv_456"
}
```

### **Document Upload**
```http
POST /upload
Content-Type: multipart/form-data

file: <your-document.pdf>
```

### **Document Management**
```http
GET /documents          # List all documents
DELETE /documents/{id}  # Remove document
```

## 🎨 Design Highlights

### **NotebookLM-Inspired Interface**
- **Authentic Google design** with carefully selected color palette
- **Typography**: Google Sans font family throughout
- **Glassmorphism**: Advanced backdrop filters and blur effects
- **Micro-interactions**: Smooth hover states and transitions
- **Dark theme**: Professional appearance with proper contrast ratios

### **Smart Document Grouping**
- **Unified document view**: No more scattered chunks
- **Intelligent aggregation**: Groups by document title and type
- **Source management**: Clean, organized document selection
- **Confidence scoring**: Shows relevance with max confidence per document
## 🚀 Deployment

### **Production Deployment**

#### **Using Docker (Recommended)**
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d --build

# Scale services
docker-compose up --scale backend=3
```

#### **Environment Configuration for Production**
```env
# Production settings
DEBUG=false
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
WEAVIATE_URL=http://weaviate:8080

# Security
CORS_ORIGINS=https://yourdomain.com
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### **Cloud Deployment Options**
- **AWS**: ECS, EC2, or Elastic Beanstalk
- **Google Cloud**: Cloud Run, GKE, or Compute Engine  
- **Azure**: Container Instances or App Service
- **Render**: Direct Docker deployment support

## 📄 License

MIT License - feel free to use this project for your own applications!

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

For questions or support, please open an issue on GitHub or contact the maintainers.

---

**Built with ❤️ using React, FastAPI, and the power of local AI models**
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
