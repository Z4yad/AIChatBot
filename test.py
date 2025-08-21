#!/usr/bin/env python3

"""
Test Script for AI Support Chatbot

This script tests various components and endpoints of the chatbot system.
"""

import asyncio
import aiohttp
import json
import sys
from typing import Dict, Any
import time


class ChatbotTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_health(self) -> bool:
        """Test the health endpoint."""
        print("🔍 Testing health endpoint...")
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check passed - Status: {data.get('status')}")
                    print(f"   LLM Provider: {data.get('llm_provider')}")
                    print(f"   Embedding Provider: {data.get('embedding_provider')}")
                    print(f"   Vector DB: {data.get('vector_db')}")
                    return True
                else:
                    print(f"❌ Health check failed - Status: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    async def test_chat(self, query: str, user_id: str = "test_user", product_version: str = None) -> Dict[str, Any]:
        """Test the chat endpoint."""
        print(f"💬 Testing chat with query: '{query}'")
        
        payload = {
            "user_id": user_id,
            "query": query
        }
        
        if product_version:
            payload["product_version"] = product_version
        
        try:
            start_time = time.time()
            async with self.session.post(
                f"{self.base_url}/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                end_time = time.time()
                
                if response.status == 200:
                    data = await response.json()
                    response_time = round((end_time - start_time) * 1000, 2)
                    
                    print(f"✅ Chat response received in {response_time}ms")
                    print(f"   Answer: {data.get('answer', '')[:100]}...")
                    print(f"   Confidence: {data.get('confidence', 0):.2f}")
                    print(f"   Sources: {len(data.get('sources', []))}")
                    print(f"   Fallback: {data.get('fallback_triggered', False)}")
                    
                    return data
                else:
                    error_text = await response.text()
                    print(f"❌ Chat request failed - Status: {response.status}")
                    print(f"   Error: {error_text}")
                    return {}
        except Exception as e:
            print(f"❌ Chat request error: {e}")
            return {}
    
    async def test_feedback(self, conversation_id: str, rating: int, feedback_text: str = None) -> bool:
        """Test the feedback endpoint."""
        print(f"👍 Testing feedback submission - Rating: {rating}")
        
        payload = {
            "conversation_id": conversation_id,
            "user_id": "test_user",
            "rating": rating
        }
        
        if feedback_text:
            payload["feedback_text"] = feedback_text
        
        try:
            async with self.session.post(
                f"{self.base_url}/feedback",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Feedback submitted successfully - ID: {data.get('feedback_id')}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Feedback submission failed - Status: {response.status}")
                    print(f"   Error: {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Feedback submission error: {e}")
            return False
    
    async def test_ingestion(self, source_type: str, filters: Dict[str, Any]) -> bool:
        """Test the ingestion endpoint."""
        print(f"📥 Testing ingestion - Source: {source_type}")
        
        payload = {
            "source_type": source_type,
            "filters": filters
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/ingest",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Ingestion completed")
                    print(f"   Documents processed: {data.get('documents_processed', 0)}")
                    print(f"   Chunks created: {data.get('chunks_created', 0)}")
                    
                    if data.get('errors'):
                        print(f"   Errors: {data['errors']}")
                    
                    return data.get('success', False)
                else:
                    error_text = await response.text()
                    print(f"❌ Ingestion failed - Status: {response.status}")
                    print(f"   Error: {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Ingestion error: {e}")
            return False
    
    async def test_analytics(self) -> bool:
        """Test the analytics endpoint."""
        print("📊 Testing analytics endpoint...")
        
        try:
            async with self.session.get(f"{self.base_url}/analytics/feedback") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Analytics data retrieved")
                    print(f"   Total feedback: {data.get('total_feedback', 0)}")
                    print(f"   Average rating: {data.get('average_rating', 0)}")
                    print(f"   Rating distribution: {data.get('rating_distribution', {})}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Analytics request failed - Status: {response.status}")
                    print(f"   Error: {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Analytics request error: {e}")
            return False


async def run_comprehensive_test():
    """Run a comprehensive test suite."""
    print("🚀 Starting comprehensive chatbot test suite...\n")
    
    async with ChatbotTester() as tester:
        # Test 1: Health check
        health_ok = await tester.test_health()
        print()
        
        if not health_ok:
            print("❌ Health check failed. Aborting tests.")
            return
        
        # Test 2: Chat functionality
        test_queries = [
            "How do I reset my password?",
            "What are the system requirements?",
            "How do I contact support?",
            "This is a completely random query that should trigger fallback"
        ]
        
        conversation_ids = []
        for query in test_queries:
            response = await tester.test_chat(query, product_version="v1.0")
            if response and "conversation_id" in response:
                conversation_ids.append(response["conversation_id"])
            print()
        
        # Test 3: Feedback submission
        if conversation_ids:
            await tester.test_feedback(conversation_ids[0], 5, "Great response!")
            await tester.test_feedback(conversation_ids[0], 2, "Could be better")
            print()
        
        # Test 4: Analytics
        await tester.test_analytics()
        print()
        
        # Test 5: Load testing (simple)
        print("⚡ Running simple load test...")
        start_time = time.time()
        tasks = []
        
        for i in range(5):  # 5 concurrent requests
            task = tester.test_chat(f"Test query {i}", f"load_test_user_{i}")
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        end_time = time.time()
        
        print(f"✅ Load test completed in {end_time - start_time:.2f} seconds")
        print()
        
        print("🎉 Test suite completed!")


async def run_quick_test():
    """Run a quick test."""
    print("⚡ Running quick test...\n")
    
    async with ChatbotTester() as tester:
        # Quick health check
        await tester.test_health()
        print()
        
        # Single chat test
        await tester.test_chat("Hello, can you help me?")
        print()
        
        print("✅ Quick test completed!")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Test AI Support Chatbot")
    parser.add_argument("--quick", action="store_true", help="Run quick test only")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL for the API")
    
    args = parser.parse_args()
    
    # Update tester base URL if provided
    if args.url != "http://localhost:8000":
        ChatbotTester.__init__ = lambda self, base_url=args.url: setattr(self, 'base_url', base_url) or setattr(self, 'session', None)
    
    if args.quick:
        asyncio.run(run_quick_test())
    else:
        asyncio.run(run_comprehensive_test())


if __name__ == "__main__":
    main()
