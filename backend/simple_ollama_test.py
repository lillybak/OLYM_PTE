#!/usr/bin/env python3
"""
Simple Ollama test with timeout
"""

import requests
import json
import time

def test_ollama():
    """Test Ollama API directly"""
    print("🧪 Testing Ollama API")
    print("=" * 30)
    
    try:
        # Simple test call
        payload = {
            "model": "qwen",
            "prompt": "Say hello in one word.",
            "stream": False
        }
        
        print("Sending request to Ollama...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:11434/api/generate", 
            json=payload,
            timeout=30  # 30 second timeout
        )
        
        end_time = time.time()
        print(f"Response time: {end_time - start_time:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Ollama API working!")
            print(f"Response: {result.get('response', 'No response')}")
        else:
            print(f"❌ Ollama API error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Ollama API timeout - model might be too slow")
    except Exception as e:
        print(f"❌ Ollama API error: {e}")

if __name__ == "__main__":
    test_ollama() 