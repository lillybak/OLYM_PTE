#!/usr/bin/env python3
"""
Simple test script to check basic imports
"""

def test_imports():
    """Test basic imports without full initialization"""
    print("🧪 Testing Basic Imports")
    print("=" * 30)
    
    try:
        import openai
        print("✅ OpenAI imported successfully")
    except Exception as e:
        print(f"❌ OpenAI import failed: {e}")
    
    try:
        from langchain_community.embeddings import OpenAIEmbeddings
        print("✅ LangChain Community embeddings imported successfully")
    except Exception as e:
        print(f"❌ LangChain Community embeddings import failed: {e}")
    
    try:
        from langchain_community.vectorstores import Qdrant
        print("✅ Qdrant vectorstore imported successfully")
    except Exception as e:
        print(f"❌ Qdrant vectorstore import failed: {e}")
    
    try:
        from qdrant_client import QdrantClient
        print("✅ Qdrant client imported successfully")
    except Exception as e:
        print(f"❌ Qdrant client import failed: {e}")
    
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        print("✅ LangChain text splitter imported successfully")
    except Exception as e:
        print(f"❌ LangChain text splitter import failed: {e}")
    
    print("\n🎉 Basic import test completed!")

if __name__ == "__main__":
    test_imports() 