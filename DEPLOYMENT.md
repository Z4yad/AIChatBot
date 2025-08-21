# Deployment Guide

## Overview

This guide covers deploying the AI Support Chatbot to various environments and platforms.

## Local Development Deployment

### Prerequisites

- Docker and Docker Compose
- 8GB+ RAM (for local LLM)
- 10GB+ disk space

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd ai-support-chatbot

# Run setup
./setup.sh

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000/docs
# Weaviate: http://localhost:8080
```

## Production Deployment Options

### Option 1: Cloud-based with Managed Services (Recommended)

**Stack:**
- Backend: Container platform (AWS ECS, Google Cloud Run, Azure Container Instances)
- LLM: OpenAI API
- Embeddings: OpenAI API
- Vector DB: Pinecone (managed)
- Frontend: Static hosting (Vercel, Netlify, AWS S3)

**Benefits:**
- Fully managed and scalable
- No model hosting required
- High availability
- Cost-effective for variable loads

### Option 2: Hybrid Cloud with Self-hosted Vector DB

**Stack:**
- Backend: Container platform
- LLM: OpenAI API
- Embeddings: OpenAI API
- Vector DB: Self-hosted Weaviate on cloud VM
- Frontend: Static hosting

**Benefits:**
- Data control with vector DB
- Managed LLM for reliability
- Cost control for vector storage

### Option 3: Fully Self-hosted

**Stack:**
- Backend: Self-hosted containers
- LLM: Self-hosted Ollama
- Embeddings: Local models
- Vector DB: Self-hosted Weaviate
- Frontend: Self-hosted

**Benefits:**
- Complete data control
- No external API dependencies
- One-time setup cost

## Platform-Specific Deployments

### AWS Deployment

#### Using AWS ECS + Fargate

1. **Build and Push Images**

```bash
# Build images
docker build -t ai-chatbot-backend ./backend
docker build -t ai-chatbot-frontend ./frontend

# Tag for ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

docker tag ai-chatbot-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/ai-chatbot-backend:latest
docker tag ai-chatbot-frontend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/ai-chatbot-frontend:latest

# Push to ECR
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/ai-chatbot-backend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/ai-chatbot-frontend:latest
```

2. **Create ECS Task Definition**

```json
{
  "family": "ai-chatbot",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::<account>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "<account>.dkr.ecr.us-east-1.amazonaws.com/ai-chatbot-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "LLM_PROVIDER",
          "value": "openai"
        },
        {
          "name": "VECTOR_DB",
          "value": "pinecone"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:<account>:secret:chatbot/openai-key"
        },
        {
          "name": "PINECONE_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:<account>:secret:chatbot/pinecone-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ai-chatbot",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

3. **Create ECS Service with Load Balancer**

```bash
# Create Application Load Balancer
aws elbv2 create-load-balancer \
  --name ai-chatbot-alb \
  --subnets subnet-12345 subnet-67890 \
  --security-groups sg-12345

# Create target group
aws elbv2 create-target-group \
  --name ai-chatbot-targets \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-12345 \
  --target-type ip

# Create ECS service
aws ecs create-service \
  --cluster ai-chatbot-cluster \
  --service-name ai-chatbot-service \
  --task-definition ai-chatbot:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345,subnet-67890],securityGroups=[sg-12345],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:<account>:targetgroup/ai-chatbot-targets/<id>,containerName=backend,containerPort=8000"
```

#### Using AWS Lambda (Serverless)

For lighter workloads, deploy the backend as Lambda functions:

```python
# lambda_handler.py
import json
from mangum import Mangum
from main import app

handler = Mangum(app)

def lambda_handler(event, context):
    return handler(event, context)
```

### Google Cloud Platform Deployment

#### Using Cloud Run

1. **Deploy Backend**

```bash
# Build and deploy backend
gcloud run deploy ai-chatbot-backend \
  --source ./backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars LLM_PROVIDER=openai,VECTOR_DB=pinecone \
  --set-secrets OPENAI_API_KEY=openai-key:latest,PINECONE_API_KEY=pinecone-key:latest
```

2. **Deploy Frontend**

```bash
# Build frontend
cd frontend
npm run build

# Deploy to Firebase Hosting
firebase deploy --only hosting
```

### Azure Deployment

#### Using Azure Container Instances

```bash
# Create resource group
az group create --name ai-chatbot-rg --location eastus

# Deploy backend container
az container create \
  --resource-group ai-chatbot-rg \
  --name ai-chatbot-backend \
  --image <registry>.azurecr.io/ai-chatbot-backend:latest \
  --dns-name-label ai-chatbot-backend \
  --ports 8000 \
  --environment-variables LLM_PROVIDER=openai VECTOR_DB=pinecone \
  --secure-environment-variables OPENAI_API_KEY=<key> PINECONE_API_KEY=<key>

# Deploy frontend to Azure Static Web Apps
az staticwebapp create \
  --name ai-chatbot-frontend \
  --resource-group ai-chatbot-rg \
  --source https://github.com/<user>/<repo> \
  --location "Central US" \
  --branch main \
  --app-location "/frontend" \
  --api-location "/backend" \
  --output-location "build"
```

## Database Setup

### Pinecone Setup (Recommended for Production)

1. **Create Pinecone Account**
   - Sign up at https://pinecone.io
   - Create a new project
   - Generate API key

2. **Create Index**

```python
import pinecone

pinecone.init(api_key="your-api-key", environment="us-east1-gcp")

# Create index
pinecone.create_index(
    name="ai-support-chatbot",
    dimension=3072,  # for text-embedding-3-large
    metric="cosine"
)
```

3. **Configure Application**

```bash
# In backend/.env
VECTOR_DB=pinecone
PINECONE_API_KEY=your-api-key
PINECONE_ENVIRONMENT=us-east1-gcp
PINECONE_INDEX_NAME=ai-support-chatbot
```

### Weaviate Setup (Self-hosted)

#### Docker Deployment

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  weaviate:
    image: semitechnologies/weaviate:1.21.8
    ports:
      - "8080:8080"
    environment:
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'false'
      AUTHENTICATION_APIKEY_ENABLED: 'true'
      AUTHENTICATION_APIKEY_ALLOWED_KEYS: 'your-secure-api-key'
      AUTHORIZATION_ADMINLIST_ENABLED: 'true'
      AUTHORIZATION_ADMINLIST_USERS: 'admin'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      QUERY_DEFAULTS_LIMIT: 25
      DEFAULT_VECTORIZER_MODULE: 'none'
      ENABLE_MODULES: ''
      CLUSTER_HOSTNAME: 'node1'
    volumes:
      - weaviate_data:/var/lib/weaviate
    restart: unless-stopped
```

#### Kubernetes Deployment

```yaml
# weaviate-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: weaviate
spec:
  replicas: 1
  selector:
    matchLabels:
      app: weaviate
  template:
    metadata:
      labels:
        app: weaviate
    spec:
      containers:
      - name: weaviate
        image: semitechnologies/weaviate:1.21.8
        ports:
        - containerPort: 8080
        env:
        - name: PERSISTENCE_DATA_PATH
          value: "/var/lib/weaviate"
        - name: QUERY_DEFAULTS_LIMIT
          value: "25"
        - name: AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED
          value: "false"
        - name: AUTHENTICATION_APIKEY_ENABLED
          value: "true"
        - name: AUTHENTICATION_APIKEY_ALLOWED_KEYS
          valueFrom:
            secretKeyRef:
              name: weaviate-secret
              key: api-key
        volumeMounts:
        - name: weaviate-storage
          mountPath: /var/lib/weaviate
      volumes:
      - name: weaviate-storage
        persistentVolumeClaim:
          claimName: weaviate-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: weaviate-service
spec:
  selector:
    app: weaviate
  ports:
  - port: 8080
    targetPort: 8080
  type: LoadBalancer
```

## Environment Configuration

### Production Environment Variables

```bash
# Backend
ENVIRONMENT=production
LOG_LEVEL=INFO

# LLM Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4o-mini

# Embeddings
EMBEDDING_PROVIDER=openai
OPENAI_EMBEDDING_MODEL=text-embedding-3-large

# Vector Database
VECTOR_DB=pinecone
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=us-east1-gcp
PINECONE_INDEX_NAME=ai-support-chatbot

# Security
SECRET_KEY=your-secure-secret-key
CORS_ORIGINS=["https://your-frontend-domain.com"]

# Performance
SIMILARITY_THRESHOLD=0.8
MAX_RETRIEVED_CHUNKS=5
CHUNK_SIZE=500

# Data Sources (optional)
ZENDESK_SUBDOMAIN=your-company
ZENDESK_EMAIL=support@your-company.com
ZENDESK_TOKEN=your-zendesk-token

JIRA_SERVER=https://your-company.atlassian.net
JIRA_EMAIL=support@your-company.com
JIRA_API_TOKEN=your-jira-token
```

```bash
# Frontend
REACT_APP_API_BASE_URL=https://your-backend-domain.com
REACT_APP_CHAT_TITLE=Customer Support Assistant
REACT_APP_WELCOME_MESSAGE=Hello! How can I help you today?
REACT_APP_PLACEHOLDER_TEXT=Ask me anything...
```

## Monitoring and Logging

### Application Monitoring

1. **Health Checks**
   - Backend: `/health` endpoint
   - Response time monitoring
   - Error rate tracking

2. **Metrics to Monitor**
   - Response time
   - Error rates
   - Token usage (OpenAI)
   - Vector database performance
   - User satisfaction (feedback ratings)

3. **Logging Setup**

```python
# logging_config.py
import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('/app/logs/app.log')
        ]
    )
```

### Infrastructure Monitoring

1. **AWS CloudWatch**
2. **Google Cloud Monitoring**
3. **Azure Monitor**
4. **Prometheus + Grafana**

## Security Considerations

### API Security

1. **API Key Management**
   - Use environment variables
   - Rotate keys regularly
   - Use cloud secret managers

2. **Authentication**
   - Implement JWT tokens for production
   - Rate limiting
   - CORS configuration

3. **Input Validation**
   - Sanitize user inputs
   - Limit query length
   - Prevent injection attacks

### Network Security

1. **HTTPS Only**
2. **Security Groups/Firewalls**
3. **VPC/Private Networks**
4. **DDoS Protection**

## Scaling Considerations

### Horizontal Scaling

1. **Backend Services**
   - Stateless design
   - Load balancer distribution
   - Auto-scaling based on CPU/memory

2. **Database Scaling**
   - Pinecone auto-scales
   - Weaviate clustering for self-hosted

### Performance Optimization

1. **Caching**
   - Redis for session storage
   - Vector result caching
   - Response caching

2. **Connection Pooling**
   - Database connections
   - HTTP client pools

3. **Async Processing**
   - Background tasks for ingestion
   - Queue-based processing

## Backup and Disaster Recovery

### Data Backup

1. **Vector Database**
   - Pinecone automatic backups
   - Weaviate manual backups

2. **Configuration Backup**
   - Environment variables
   - API keys in secure storage

### Disaster Recovery

1. **Multi-region Deployment**
2. **Database Replication**
3. **Automated Failover**
4. **Recovery Testing**

## Cost Optimization

### OpenAI Costs

1. **Token Usage Monitoring**
2. **Model Selection** (gpt-4o-mini vs gpt-4)
3. **Context Optimization**
4. **Caching Strategies**

### Infrastructure Costs

1. **Right-sizing Instances**
2. **Spot Instances** (where appropriate)
3. **Auto-scaling**
4. **Resource Monitoring**

## Maintenance

### Regular Tasks

1. **Security Updates**
2. **Dependency Updates**
3. **Performance Monitoring**
4. **Data Quality Checks**

### Automated Tasks

```bash
# Update script
#!/bin/bash
set -e

echo "Starting maintenance..."

# Update dependencies
docker-compose exec backend pip install -r requirements.txt --upgrade
docker-compose exec frontend npm update

# Restart services
docker-compose restart

# Run health checks
./test.py --quick

echo "Maintenance completed"
```

This comprehensive deployment guide covers all aspects of deploying the AI Support Chatbot in various environments, from local development to enterprise production deployments.
