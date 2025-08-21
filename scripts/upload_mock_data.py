#!/usr/bin/env python3
"""
Mock data upload script for AI Support Chatbot

This script uploads mock data files to populate the knowledge base for testing.
"""

import asyncio
import aiohttp
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# Configuration
API_BASE_URL = "http://localhost:8000"
MOCK_DATA_DIR = Path(__file__).parent.parent / "mock_data"

class MockDataUploader:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def check_api_health(self) -> bool:
        """Check if the API is running and healthy."""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ API is healthy: {data.get('status')}")
                    return True
                else:
                    print(f"❌ API health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Could not connect to API: {e}")
            return False
    
    async def upload_file(self, file_path: Path, **kwargs) -> Dict[str, Any]:
        """Upload a file to the API."""
        try:
            data = aiohttp.FormData()
            
            # Add file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            data.add_field('file', file_content, filename=file_path.name)
            
            # Add optional fields
            for key, value in kwargs.items():
                if value:
                    data.add_field(key, value)
            
            async with self.session.post(f"{self.base_url}/upload/file", data=data) as response:
                result = await response.json()
                
                if response.status == 200:
                    print(f"✅ Uploaded {file_path.name}: {result.get('message')}")
                    return result
                else:
                    print(f"❌ Failed to upload {file_path.name}: {result.get('detail')}")
                    return result
                    
        except Exception as e:
            print(f"❌ Error uploading {file_path.name}: {e}")
            return {"error": str(e)}
    
    async def upload_json_data(self, file_path: Path, data_type: str, **kwargs) -> Dict[str, Any]:
        """Upload JSON data to the API."""
        try:
            data = aiohttp.FormData()
            
            # Add file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            data.add_field('file', file_content, filename=file_path.name)
            
            # Add data type
            data.add_field('data_type', data_type)
            
            # Add optional fields
            for key, value in kwargs.items():
                if value:
                    data.add_field(key, value)
            
            async with self.session.post(f"{self.base_url}/upload/json", data=data) as response:
                result = await response.json()
                
                if response.status == 200:
                    print(f"✅ Uploaded {file_path.name} ({data_type}): {result.get('message')}")
                    return result
                else:
                    print(f"❌ Failed to upload {file_path.name}: {result.get('detail')}")
                    return result
                    
        except Exception as e:
            print(f"❌ Error uploading {file_path.name}: {e}")
            return {"error": str(e)}

async def main():
    """Main upload function."""
    print("🚀 Starting mock data upload...")
    print(f"📁 Mock data directory: {MOCK_DATA_DIR}")
    print(f"🌐 API URL: {API_BASE_URL}")
    print("-" * 50)
    
    # Check if mock data directory exists
    if not MOCK_DATA_DIR.exists():
        print(f"❌ Mock data directory not found: {MOCK_DATA_DIR}")
        return
    
    async with MockDataUploader() as uploader:
        # Check API health
        if not await uploader.check_api_health():
            print("❌ API is not available. Please start the backend service.")
            return
        
        print("\n📄 Uploading document files...")
        
        # Upload document files
        document_files = [
            ("sample_documentation.docx", {
                "title": "API Documentation",
                "product_version": "v2.1.0",
                "tags": "api,documentation,reference"
            }),
            ("api_documentation.md", {
                "title": "API Reference Guide",
                "product_version": "v2.1.0", 
                "tags": "api,endpoints,authentication"
            }),
            ("troubleshooting_guide.md", {
                "title": "Troubleshooting Guide",
                "product_version": "v2.1.0",
                "tags": "troubleshooting,issues,solutions"
            })
        ]
        
        for filename, metadata in document_files:
            file_path = MOCK_DATA_DIR / filename
            if file_path.exists():
                await uploader.upload_file(file_path, **metadata)
            else:
                print(f"⚠️  File not found: {filename}")
        
        print("\n📊 Uploading JSON data...")
        
        # Upload JSON data
        json_files = [
            ("helpdesk_tickets.json", "helpdesk", {"product_version": "v2.1.0"}),
            ("zendesk_tickets.json", "zendesk", {"product_version": "v2.1.0"})
        ]
        
        for filename, data_type, metadata in json_files:
            file_path = MOCK_DATA_DIR / filename
            if file_path.exists():
                await uploader.upload_json_data(file_path, data_type, **metadata)
            else:
                print(f"⚠️  File not found: {filename}")
        
        print("\n✅ Mock data upload completed!")
        print("\n💡 You can now test the chatbot with questions like:")
        print("   • 'How do I authenticate with the API?'")
        print("   • 'What are the rate limits?'") 
        print("   • 'How to fix connection timeout issues?'")
        print("   • 'Tell me about webhook configuration'")

def create_sample_files():
    """Create sample files if they don't exist."""
    print("📝 Creating sample mock data files...")
    
    # Ensure mock_data directory exists
    MOCK_DATA_DIR.mkdir(exist_ok=True)
    
    # Create a simple API documentation markdown file if it doesn't exist
    api_doc_path = MOCK_DATA_DIR / "api_documentation.md"
    if not api_doc_path.exists():
        api_content = """# API Quick Start Guide

## Authentication
Use Bearer tokens for API authentication:
```
Authorization: Bearer YOUR_API_KEY
```

## Rate Limits
- Free tier: 100 requests/hour
- Pro tier: 1000 requests/hour
- Enterprise: 10000 requests/hour

## Common Endpoints
- GET /api/users - List users
- POST /api/users - Create user
- GET /api/orders - List orders
- POST /api/orders - Create order

## Error Codes
- 400: Bad Request
- 401: Unauthorized  
- 429: Rate Limited
- 500: Server Error
"""
        with open(api_doc_path, 'w') as f:
            f.write(api_content)
        print(f"✅ Created {api_doc_path.name}")

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--create-samples":
        create_sample_files()
        print("Sample files created. Run the script again without --create-samples to upload.")
        sys.exit(0)
    
    # Run the upload
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Upload cancelled by user")
    except Exception as e:
        print(f"\n❌ Upload failed: {e}")
        sys.exit(1)