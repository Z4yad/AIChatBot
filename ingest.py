#!/usr/bin/env python3

"""
Data Ingestion Script for AI Support Chatbot

This script provides a command-line interface for ingesting data
from various sources into the chatbot's vector database.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent / "backend"))

from app.services.ingestion import ingestion_service
from app.services.vector_store import vector_store
from app.models import DocumentSource


async def ingest_pdf(file_path: str, title: str = None, product_version: str = None, tags: List[str] = None):
    """Ingest a PDF document."""
    filters = {
        "file_path": file_path,
        "title": title or f"PDF Document - {Path(file_path).name}",
        "product_version": product_version,
        "tags": tags or []
    }
    
    print(f"📄 Ingesting PDF: {file_path}")
    chunks = await ingestion_service.ingest_documents(DocumentSource.PDF, filters)
    
    if chunks:
        print(f"💾 Storing {len(chunks)} chunks in vector database...")
        await vector_store.upsert_chunks(chunks)
        print(f"✅ Successfully ingested {len(chunks)} chunks from PDF")
    else:
        print("❌ No chunks generated from PDF")


async def ingest_docx(file_path: str, title: str = None, product_version: str = None, tags: List[str] = None):
    """Ingest a Word document."""
    filters = {
        "file_path": file_path,
        "title": title or f"Word Document - {Path(file_path).name}",
        "product_version": product_version,
        "tags": tags or []
    }
    
    print(f"📄 Ingesting DOCX: {file_path}")
    chunks = await ingestion_service.ingest_documents(DocumentSource.DOCX, filters)
    
    if chunks:
        print(f"💾 Storing {len(chunks)} chunks in vector database...")
        await vector_store.upsert_chunks(chunks)
        print(f"✅ Successfully ingested {len(chunks)} chunks from DOCX")
    else:
        print("❌ No chunks generated from DOCX")


async def ingest_zendesk(limit: int = 100, product_version: str = None):
    """Ingest Zendesk tickets."""
    filters = {
        "limit": limit,
        "product_version": product_version
    }
    
    print(f"🎫 Ingesting {limit} Zendesk tickets...")
    chunks = await ingestion_service.ingest_documents(DocumentSource.ZENDESK, filters)
    
    if chunks:
        print(f"💾 Storing {len(chunks)} chunks in vector database...")
        await vector_store.upsert_chunks(chunks)
        print(f"✅ Successfully ingested {len(chunks)} chunks from Zendesk")
    else:
        print("❌ No chunks generated from Zendesk")


async def ingest_jira(jql: str = "project is not EMPTY", limit: int = 100, product_version: str = None):
    """Ingest Jira issues."""
    filters = {
        "jql": jql,
        "limit": limit,
        "product_version": product_version
    }
    
    print(f"🐛 Ingesting Jira issues with JQL: {jql}")
    chunks = await ingestion_service.ingest_documents(DocumentSource.JIRA, filters)
    
    if chunks:
        print(f"💾 Storing {len(chunks)} chunks in vector database...")
        await vector_store.upsert_chunks(chunks)
        print(f"✅ Successfully ingested {len(chunks)} chunks from Jira")
    else:
        print("❌ No chunks generated from Jira")


async def ingest_from_config(config_file: str):
    """Ingest from a configuration file."""
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    for source_config in config.get("sources", []):
        source_type = DocumentSource(source_config["source_type"])
        filters = source_config.get("filters", {})
        
        print(f"📥 Ingesting from {source_type.value}...")
        try:
            chunks = await ingestion_service.ingest_documents(source_type, filters)
            
            if chunks:
                await vector_store.upsert_chunks(chunks)
                print(f"✅ Successfully ingested {len(chunks)} chunks from {source_type.value}")
            else:
                print(f"❌ No chunks generated from {source_type.value}")
        except Exception as e:
            print(f"❌ Error ingesting from {source_type.value}: {e}")


async def main():
    parser = argparse.ArgumentParser(description="Ingest data into AI Support Chatbot")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # PDF ingestion
    pdf_parser = subparsers.add_parser("pdf", help="Ingest PDF document")
    pdf_parser.add_argument("file_path", help="Path to PDF file")
    pdf_parser.add_argument("--title", help="Document title")
    pdf_parser.add_argument("--product-version", help="Product version")
    pdf_parser.add_argument("--tags", nargs="*", help="Document tags")
    
    # DOCX ingestion
    docx_parser = subparsers.add_parser("docx", help="Ingest Word document")
    docx_parser.add_argument("file_path", help="Path to DOCX file")
    docx_parser.add_argument("--title", help="Document title")
    docx_parser.add_argument("--product-version", help="Product version")
    docx_parser.add_argument("--tags", nargs="*", help="Document tags")
    
    # Zendesk ingestion
    zendesk_parser = subparsers.add_parser("zendesk", help="Ingest Zendesk tickets")
    zendesk_parser.add_argument("--limit", type=int, default=100, help="Number of tickets to ingest")
    zendesk_parser.add_argument("--product-version", help="Product version")
    
    # Jira ingestion
    jira_parser = subparsers.add_parser("jira", help="Ingest Jira issues")
    jira_parser.add_argument("--jql", default="project is not EMPTY", help="JQL query")
    jira_parser.add_argument("--limit", type=int, default=100, help="Number of issues to ingest")
    jira_parser.add_argument("--product-version", help="Product version")
    
    # Config file ingestion
    config_parser = subparsers.add_parser("config", help="Ingest from configuration file")
    config_parser.add_argument("config_file", help="Path to JSON configuration file")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize vector store
    print("🔌 Initializing vector store...")
    await vector_store.initialize()
    
    try:
        if args.command == "pdf":
            await ingest_pdf(
                args.file_path,
                args.title,
                args.product_version,
                args.tags
            )
        elif args.command == "docx":
            await ingest_docx(
                args.file_path,
                args.title,
                args.product_version,
                args.tags
            )
        elif args.command == "zendesk":
            await ingest_zendesk(args.limit, args.product_version)
        elif args.command == "jira":
            await ingest_jira(args.jql, args.limit, args.product_version)
        elif args.command == "config":
            await ingest_from_config(args.config_file)
    
    except Exception as e:
        print(f"❌ Error during ingestion: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
