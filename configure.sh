#!/bin/bash

# Configuration Management Script
set -e

BACKEND_ENV="backend/.env"
FRONTEND_ENV="frontend/.env"

show_help() {
    echo "AI Support Chatbot Configuration Manager"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  switch-llm <provider>    Switch LLM provider (ollama|openai)"
    echo "  switch-embeddings <provider>    Switch embedding provider (local|openai)"
    echo "  switch-vectordb <provider>    Switch vector database (weaviate|pinecone)"
    echo "  set-openai-key <key>     Set OpenAI API key"
    echo "  set-pinecone-key <key>   Set Pinecone API key"
    echo "  show-config              Show current configuration"
    echo "  validate                 Validate configuration"
    echo "  help                     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 switch-llm openai"
    echo "  $0 set-openai-key sk-your-key-here"
    echo "  $0 show-config"
}

update_env_var() {
    local file=$1
    local key=$2
    local value=$3
    
    if grep -q "^${key}=" "$file"; then
        # Update existing key
        sed -i.bak "s|^${key}=.*|${key}=${value}|" "$file"
    else
        # Add new key
        echo "${key}=${value}" >> "$file"
    fi
    echo "✅ Updated ${key} in ${file}"
}

switch_llm() {
    local provider=$1
    if [[ "$provider" != "ollama" && "$provider" != "openai" ]]; then
        echo "❌ Invalid LLM provider. Use 'ollama' or 'openai'"
        exit 1
    fi
    
    update_env_var "$BACKEND_ENV" "LLM_PROVIDER" "$provider"
    
    if [[ "$provider" == "openai" ]]; then
        echo "⚠️  Don't forget to set your OpenAI API key:"
        echo "   $0 set-openai-key YOUR_KEY_HERE"
    fi
    
    echo "🔄 Restart the backend service to apply changes:"
    echo "   docker-compose restart backend"
}

switch_embeddings() {
    local provider=$1
    if [[ "$provider" != "local" && "$provider" != "openai" ]]; then
        echo "❌ Invalid embedding provider. Use 'local' or 'openai'"
        exit 1
    fi
    
    update_env_var "$BACKEND_ENV" "EMBEDDING_PROVIDER" "$provider"
    
    if [[ "$provider" == "openai" ]]; then
        echo "⚠️  Don't forget to set your OpenAI API key:"
        echo "   $0 set-openai-key YOUR_KEY_HERE"
    fi
    
    echo "🔄 Restart the backend service to apply changes:"
    echo "   docker-compose restart backend"
}

switch_vectordb() {
    local provider=$1
    if [[ "$provider" != "weaviate" && "$provider" != "pinecone" ]]; then
        echo "❌ Invalid vector database. Use 'weaviate' or 'pinecone'"
        exit 1
    fi
    
    update_env_var "$BACKEND_ENV" "VECTOR_DB" "$provider"
    
    if [[ "$provider" == "pinecone" ]]; then
        echo "⚠️  Don't forget to set your Pinecone credentials:"
        echo "   $0 set-pinecone-key YOUR_KEY_HERE"
        echo "   And update PINECONE_ENVIRONMENT in $BACKEND_ENV"
    fi
    
    echo "🔄 Restart the backend service to apply changes:"
    echo "   docker-compose restart backend"
}

set_openai_key() {
    local key=$1
    if [[ -z "$key" ]]; then
        echo "❌ Please provide an OpenAI API key"
        exit 1
    fi
    
    update_env_var "$BACKEND_ENV" "OPENAI_API_KEY" "$key"
    echo "🔄 Restart the backend service to apply changes:"
    echo "   docker-compose restart backend"
}

set_pinecone_key() {
    local key=$1
    if [[ -z "$key" ]]; then
        echo "❌ Please provide a Pinecone API key"
        exit 1
    fi
    
    update_env_var "$BACKEND_ENV" "PINECONE_API_KEY" "$key"
    echo "⚠️  Also update PINECONE_ENVIRONMENT in $BACKEND_ENV"
    echo "🔄 Restart the backend service to apply changes:"
    echo "   docker-compose restart backend"
}

show_config() {
    echo "🔧 Current Configuration:"
    echo ""
    
    if [[ -f "$BACKEND_ENV" ]]; then
        echo "Backend Configuration:"
        echo "  LLM Provider: $(grep '^LLM_PROVIDER=' $BACKEND_ENV | cut -d'=' -f2)"
        echo "  Embedding Provider: $(grep '^EMBEDDING_PROVIDER=' $BACKEND_ENV | cut -d'=' -f2)"
        echo "  Vector Database: $(grep '^VECTOR_DB=' $BACKEND_ENV | cut -d'=' -f2)"
        echo "  OpenAI Key: $(grep '^OPENAI_API_KEY=' $BACKEND_ENV | cut -d'=' -f2 | sed 's/\(sk-[a-zA-Z0-9]\{4\}\).*\([a-zA-Z0-9]\{4\}\)/\1...\2/')"
        echo "  Pinecone Key: $(grep '^PINECONE_API_KEY=' $BACKEND_ENV | cut -d'=' -f2 | sed 's/\([a-zA-Z0-9]\{4\}\).*\([a-zA-Z0-9]\{4\}\)/\1...\2/')"
    else
        echo "❌ Backend .env file not found"
    fi
    
    echo ""
}

validate_config() {
    echo "🔍 Validating configuration..."
    
    if [[ ! -f "$BACKEND_ENV" ]]; then
        echo "❌ Backend .env file not found. Run setup.sh first."
        exit 1
    fi
    
    local llm_provider=$(grep '^LLM_PROVIDER=' $BACKEND_ENV | cut -d'=' -f2)
    local embedding_provider=$(grep '^EMBEDDING_PROVIDER=' $BACKEND_ENV | cut -d'=' -f2)
    local vector_db=$(grep '^VECTOR_DB=' $BACKEND_ENV | cut -d'=' -f2)
    local openai_key=$(grep '^OPENAI_API_KEY=' $BACKEND_ENV | cut -d'=' -f2)
    local pinecone_key=$(grep '^PINECONE_API_KEY=' $BACKEND_ENV | cut -d'=' -f2)
    
    # Validate LLM provider
    if [[ "$llm_provider" == "openai" && -z "$openai_key" ]]; then
        echo "❌ OpenAI LLM provider selected but no API key set"
        exit 1
    fi
    
    # Validate embedding provider
    if [[ "$embedding_provider" == "openai" && -z "$openai_key" ]]; then
        echo "❌ OpenAI embedding provider selected but no API key set"
        exit 1
    fi
    
    # Validate vector database
    if [[ "$vector_db" == "pinecone" && -z "$pinecone_key" ]]; then
        echo "❌ Pinecone vector database selected but no API key set"
        exit 1
    fi
    
    echo "✅ Configuration is valid"
}

# Main command processing
case "${1:-help}" in
    "switch-llm")
        switch_llm "$2"
        ;;
    "switch-embeddings")
        switch_embeddings "$2"
        ;;
    "switch-vectordb")
        switch_vectordb "$2"
        ;;
    "set-openai-key")
        set_openai_key "$2"
        ;;
    "set-pinecone-key")
        set_pinecone_key "$2"
        ;;
    "show-config")
        show_config
        ;;
    "validate")
        validate_config
        ;;
    "help"|*)
        show_help
        ;;
esac
