#!/usr/bin/env python3
"""
Utility script to upload and process documents for the RAG system
"""

import os
import sys
from pathlib import Path
from rag_system import initialize_rag_system

def main():
    """Main function to upload documents"""
    print("📚 NPTE RAG Document Upload Utility")
    print("=" * 50)
    
    # Initialize RAG system
    try:
        rag_system = initialize_rag_system()
        print("✅ RAG system initialized")
    except Exception as e:
        print(f"❌ Failed to initialize RAG system: {e}")
        return
    
    # Check documents directory
    documents_path = Path("documents")
    if not documents_path.exists():
        documents_path.mkdir()
        print(f"📁 Created documents directory: {documents_path}")
        print("Please add your NPTE materials to this directory and run again.")
        return
    
    # List available files
    files = list(documents_path.rglob("*"))
    if not files:
        print("📁 No files found in documents directory")
        print("Please add your NPTE materials (PDF, DOCX, TXT) to the 'documents' folder")
        return
    
    print(f"📄 Found {len(files)} files in documents directory:")
    for file in files:
        if file.is_file():
            print(f"  - {file.name}")
    
    # Process documents
    print("\n🔄 Processing documents...")
    try:
        rag_system.load_documents_from_directory(str(documents_path))
        print("✅ Documents processed successfully!")
        print("\n🎯 Your RAG system is now ready to generate MCQs with your materials!")
        
    except Exception as e:
        print(f"❌ Error processing documents: {e}")
        return
    
    print("\n📋 Next steps:")
    print("1. Start your backend: uvicorn app:app --reload --host 0.0.0.0 --port 8000")
    print("2. Start your frontend: npm run dev")
    print("3. Try generating MCQs - they'll now use your uploaded materials!")

if __name__ == "__main__":
    main() 