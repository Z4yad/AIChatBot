#!/bin/bash

# AI Support Chatbot Setup Script
set -e

echo "🚀 Setting up AI Support Chatbot..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker and try again."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

# Create environment files if they don't exist
echo "📝 Setting up environment files..."

if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env from template"
    echo "⚠️  Please edit backend/.env with your API keys and settings"
fi

if [ ! -f "frontend/.env" ]; then
    cp frontend/.env.example frontend/.env
    echo "✅ Created frontend/.env from template"
fi

# Create data directory for local file storage
mkdir -p data/documents
mkdir -p data/logs

echo "🐳 Starting services with Docker Compose..."

# Start services
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if Ollama is running and pull the model
echo "🤖 Setting up Ollama with Llama 3.2..."
docker-compose exec ollama ollama pull llama3.2 || {
    echo "⚠️  Ollama model pull failed. You can run this manually later:"
    echo "   docker-compose exec ollama ollama pull llama3.2"
}

# Check service health
echo "🔍 Checking service health..."

# Check backend health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "⚠️  Backend health check failed"
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is accessible"
else
    echo "⚠️  Frontend is not accessible yet (may still be building)"
fi

# Check Weaviate
if curl -f http://localhost:8080/v1/.well-known/ready > /dev/null 2>&1; then
    echo "✅ Weaviate is ready"
else
    echo "⚠️  Weaviate is not ready yet"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📚 Next steps:"
echo "1. Edit backend/.env with your API keys (Pinecone, OpenAI, Zendesk, Jira)"
echo "2. Access the application:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Weaviate: http://localhost:8080"
echo ""
echo "📖 To ingest data:"
echo "   curl -X POST http://localhost:8000/ingest \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"source_type\": \"pdf\", \"filters\": {\"file_path\": \"/path/to/file.pdf\"}}'"
echo ""
echo "🛠️  Useful commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Stop services: docker-compose down"
echo "   - Restart services: docker-compose restart"
echo "   - Pull Ollama model: docker-compose exec ollama ollama pull llama3.2"
