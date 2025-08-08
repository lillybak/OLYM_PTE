#!/usr/bin/env python3
"""
Script to check Qdrant vector store data and count loaded files
"""

from qdrant_client import QdrantClient
from rag_system import initialize_rag_system
import json

def check_qdrant_data():
    """Check if there's data in the Qdrant vector store"""
    
    # Initialize Qdrant client
    qdrant_path = "./qdrant_data"
    client = QdrantClient(path=qdrant_path)
    
    print("🔍 Checking Qdrant Vector Store...")
    print(f"📁 Storage path: {qdrant_path}")
    
    # Check collections
    try:
        collections = client.get_collections()
        print(f"\n📊 Collections found: {len(collections.collections)}")
        
        for collection in collections.collections:
            print(f"  - {collection.name}")
            
            # Get collection info
            collection_info = client.get_collection(collection.name)
            print(f"    Points count: {collection_info.points_count}")
            print(f"    Vectors count: {collection_info.vectors_count}")
            
            # Get some sample points to see what's stored
            if collection_info.points_count > 0:
                print(f"    Status: ✅ Has data")
                
                # Get sample points to see metadata
                points = client.scroll(
                    collection_name=collection.name,
                    limit=5,
                    with_payload=True,
                    with_vectors=False
                )
                
                print(f"    Sample files loaded:")
                unique_sources = set()
                for point in points[0]:
                    if 'payload' in point and 'source' in point['payload']:
                        source = point['payload']['source']
                        unique_sources.add(source)
                
                for source in list(unique_sources)[:5]:  # Show first 5 unique sources
                    print(f"      - {source}")
                
                if len(unique_sources) > 5:
                    print(f"      ... and {len(unique_sources) - 5} more files")
                    
            else:
                print(f"    Status: ❌ Empty")
                
    except Exception as e:
        print(f"❌ Error checking Qdrant: {e}")
        return False
    
    return True

def check_rag_system():
    """Check RAG system status"""
    print("\n🔍 Checking RAG System...")
    
    try:
        rag = initialize_rag_system()
        print("✅ RAG system initialized successfully")
        
        # Check if vector store has data
        if rag.vector_store:
            print("✅ Vector store is available")
            
            # Try to get some documents
            try:
                docs = rag.vector_store.similarity_search("NPTE", k=1)
                if docs:
                    print(f"✅ Vector store has {len(docs)} document(s) available")
                    return True
                else:
                    print("❌ Vector store is empty")
                    return False
            except Exception as e:
                print(f"❌ Error querying vector store: {e}")
                return False
        else:
            print("❌ Vector store not available")
            return False
            
    except Exception as e:
        print(f"❌ Error initializing RAG system: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 QDRANT VECTOR STORE STATUS CHECK")
    print("=" * 60)
    
    # Check Qdrant directly
    qdrant_ok = check_qdrant_data()
    
    # Check RAG system
    rag_ok = check_rag_system()
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    
    if qdrant_ok and rag_ok:
        print("✅ Vector store has data and RAG system is working")
    elif qdrant_ok and not rag_ok:
        print("⚠️ Vector store has data but RAG system has issues")
    elif not qdrant_ok and rag_ok:
        print("⚠️ RAG system works but vector store is empty")
    else:
        print("❌ Both vector store and RAG system have issues")
    
    print("\n💡 To load documents, run:")
    print("   python -c \"from rag_system import initialize_rag_system; rag = initialize_rag_system(); rag.load_documents_from_directory('./documents/')\"") 