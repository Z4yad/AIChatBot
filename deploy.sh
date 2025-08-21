#!/bin/bash

# AI Support Chatbot Docker Deployment Script
# Usage: ./deploy.sh [dev|prod] [build]

set -e

ENVIRONMENT=${1:-dev}
BUILD_FLAG=${2:-}

echo "🚀 AI Support Chatbot Deployment"
echo "Environment: $ENVIRONMENT"
echo "=================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker compose > /dev/null 2>&1; then
    print_error "Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p data uploads nginx/ssl

# Set environment variables
export COMPOSE_PROJECT_NAME="ai-support-chatbot"

if [ "$ENVIRONMENT" = "prod" ]; then
    print_status "Deploying in PRODUCTION mode..."
    
    # Check for required environment variables
    if [ -z "$SECRET_KEY" ]; then
        print_warning "SECRET_KEY not set. Using default (not recommended for production)."
        export SECRET_KEY="change-this-in-production-$(date +%s)"
    fi
    
    if [ -z "$WEAVIATE_API_KEY" ]; then
        print_warning "WEAVIATE_API_KEY not set. Using default (not secure)."
        export WEAVIATE_API_KEY="default-api-key"
    fi
    
    COMPOSE_FILES="-f docker-compose.yml -f docker-compose.prod.yml"
    
    # Build if requested or if images don't exist
    if [ "$BUILD_FLAG" = "build" ] || [ -z "$(docker images -q ai-support-chatbot-backend 2> /dev/null)" ]; then
        print_status "Building production images..."
        docker compose $COMPOSE_FILES build --no-cache
    fi
    
else
    print_status "Deploying in DEVELOPMENT mode..."
    COMPOSE_FILES="-f docker-compose.yml"
    
    # Build if requested
    if [ "$BUILD_FLAG" = "build" ]; then
        print_status "Building development images..."
        docker compose $COMPOSE_FILES build
    fi
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker compose $COMPOSE_FILES down

# Start services
print_status "Starting services..."
docker compose $COMPOSE_FILES up -d

# Wait for services to be healthy
print_status "Waiting for services to be ready..."
sleep 10

# Check service health
check_service() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            print_success "$service is healthy"
            return 0
        fi
        
        print_status "Waiting for $service... (attempt $attempt/$max_attempts)"
        sleep 5
        attempt=$((attempt + 1))
    done
    
    print_error "$service failed to become healthy"
    return 1
}

# Health checks
print_status "Performing health checks..."

if ! check_service "Weaviate" "http://localhost:8080/v1/.well-known/ready"; then
    exit 1
fi

if ! check_service "Ollama" "http://localhost:11434/api/tags"; then
    exit 1
fi

if ! check_service "Backend" "http://localhost:8000/health"; then
    exit 1
fi

if ! check_service "Frontend" "http://localhost:3000"; then
    exit 1
fi

# Check if Ollama has models
print_status "Checking Ollama models..."
if ! docker exec ai-support-chatbot-ollama-1 ollama list | grep -q "llama3.2"; then
    print_warning "Llama3.2 model not found. Pulling model..."
    docker exec ai-support-chatbot-ollama-1 ollama pull llama3.2
    print_success "Llama3.2 model pulled successfully"
fi

# Display deployment information
echo ""
print_success "🎉 Deployment completed successfully!"
echo ""
echo "📋 Service Information:"
echo "======================="
echo "Frontend:  http://localhost:3000"
echo "Backend:   http://localhost:8000"
echo "API Docs:  http://localhost:8000/docs"
echo "Weaviate:  http://localhost:8080"
echo "Ollama:    http://localhost:11434"

if [ "$ENVIRONMENT" = "prod" ]; then
    echo "Nginx:     http://localhost (reverse proxy)"
    echo "Redis:     localhost:6379"
fi

echo ""
echo "🔍 Useful commands:"
echo "==================="
echo "View logs:       docker compose $COMPOSE_FILES logs -f"
echo "Stop services:   docker compose $COMPOSE_FILES down"
echo "Restart:         docker compose $COMPOSE_FILES restart"
echo "Shell access:    docker compose $COMPOSE_FILES exec [service] /bin/bash"
echo ""

# Show running containers
print_status "Running containers:"
docker compose $COMPOSE_FILES ps
