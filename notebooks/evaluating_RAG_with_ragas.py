#!/usr/bin/env python3
"""
Evaluating Agents with RAGAS - AI Makerspace

This script demonstrates:
1. Setting up RAGAS for agent evaluation
2. Creating synthetic test data
3. Evaluating RAG chains with different metrics
4. Comparing agent performance

Based on the AI Makerspace notebook for evaluating RAG systems.
"""

import os
import sys
import getpass
from uuid import uuid4
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path for RAG system integration
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Set up environment variables
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"] = f"RAGAS-Evaluation-{uuid4().hex[0:8]}"

# ============================================================================
# Dependencies and Setup
# ============================================================================

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    # Note: In a real environment, these would be installed via pip
    # !pip install -qU ragas==0.2.10
    # !pip install -qU langchain-community==0.3.14 langchain-openai==0.2.14
    # !pip install -qU unstructured==0.16.12 langgraph==0.2.61 langchain-qdrant==0.2.0
    print("Dependencies would be installed here")

def setup_ragas_components():
    """Set up RAGAS components for evaluation using Ollama"""
    from ragas.llms import LangchainLLMWrapper
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from langchain_community.llms import Ollama
    from langchain_ollama import OllamaEmbeddings
    
    # Use Ollama models from your current project - same as RAG system
    generator_llm = LangchainLLMWrapper(Ollama(model="qwen:latest"))
    generator_embeddings = LangchainEmbeddingsWrapper(OllamaEmbeddings(model="nomic-embed-text:latest"))
    
    print("✅ RAGAS components configured to use same models as RAG system")
    print(f"   - LLM: qwen:latest")
    print(f"   - Embeddings: nomic-embed-text:latest")
    
    return generator_llm, generator_embeddings

# ============================================================================
# Document Loading and RAG System Integration
# ============================================================================

def load_documents():
    """Load documents using the existing RAG system"""
    from rag_system import NPTERAGSystem
    
    # Initialize the RAG system (this will connect to existing Qdrant collection)
    rag_system = NPTERAGSystem()
    # Set the correct path to the Qdrant data in the backend folder
    rag_system.qdrant_client = rag_system.qdrant_client.__class__(path="../backend/qdrant_data")
    rag_system.setup_collection()
    
    # Check if documents are already in the vector store
    try:
        # Try to retrieve some documents to verify the vector store is populated
        test_docs = rag_system.retrieve_relevant_context("therapy", k=5)
        if test_docs:
            print(f"✅ Connected to existing vector store with {len(test_docs)} sample documents")
            print("Using pre-embedded documents from Qdrant collection")
            return rag_system
        else:
            print("⚠️ Vector store appears to be empty, but continuing...")
            return rag_system
    except Exception as e:
        print(f"⚠️ Error checking vector store: {e}")
        print("Continuing with RAG system...")
        return rag_system

# ============================================================================
# Synthetic Data Generation
# ============================================================================

def create_knowledge_graph(docs, generator_llm, generator_embeddings):
    """Create knowledge graph from documents"""
    from ragas.testset.graph import KnowledgeGraph, Node, NodeType
    
    print("Creating knowledge graph...")
    kg = KnowledgeGraph()
    
    # Use a subset of data for cost/time efficiency
    for doc in docs[:20]:
        kg.nodes.append(
            Node(
                type=NodeType.DOCUMENT,
                properties={"page_content": doc.page_content, "document_metadata": doc.metadata}
            )
        )
    
    print(f"Added {len(kg.nodes)} nodes to knowledge graph")
    return kg

def apply_transformations(kg, docs, generator_llm, generator_embeddings):
    """Apply default transformations to knowledge graph"""
    from ragas.testset.transforms import default_transforms, apply_transforms
    
    print("Applying transformations...")
    transformer_llm = generator_llm
    embedding_model = generator_embeddings
    
    default_transforms = default_transforms(documents=docs, llm=transformer_llm, embedding_model=embedding_model)
    apply_transforms(kg, default_transforms)
    
    return kg

def generate_synthetic_data(docs, generator_llm, generator_embeddings, testset_size=10):
    """Generate synthetic data using RAGAS"""
    from ragas.testset import TestsetGenerator
    
    print("Generating synthetic data using RAGAS...")
    generator = TestsetGenerator(llm=generator_llm, embedding_model=generator_embeddings)
    
    # Use a smaller subset and smaller test size to avoid hanging
    dataset = generator.generate_with_langchain_docs(docs[:5], testset_size=testset_size)
    return dataset

# ============================================================================
# RAG Chain Setup
# ============================================================================

def setup_basic_rag_chain(rag_system):
    """Set up basic RAG chain using existing RAG system"""
    from langchain.prompts import ChatPromptTemplate
    from langchain_community.llms import Ollama
    from operator import itemgetter
    from langchain_core.runnables import RunnablePassthrough
    from langchain.schema import StrOutputParser
    
    print("Setting up basic RAG chain using existing RAG system...")
    
    # Use the existing retriever from RAG system
    retriever = rag_system.retriever
    
    # Create prompt
    RAG_PROMPT = """\
Given a provided context and question, you must answer the question based only on context.

If you cannot answer the question based on the context - you must say "I don't know".

Context: {context}
Question: {question}
"""
    rag_prompt = ChatPromptTemplate.from_template(RAG_PROMPT)
    
    # Create LLM using Ollama
    llm = Ollama(model="qwen:latest")
    
    # Create RAG chain
    rag_chain = (
        {"context": itemgetter("question") | retriever, "question": itemgetter("question")}
        | rag_prompt | llm | StrOutputParser()
    )
    
    return rag_chain

def setup_improved_rag_chain(rag_system):
    """Set up improved RAG chain with empathy using existing RAG system"""
    from langchain.prompts import ChatPromptTemplate
    from langchain_community.llms import Ollama
    from operator import itemgetter
    from langchain_core.runnables import RunnablePassthrough
    from langchain.schema import StrOutputParser
    
    print("Setting up improved RAG chain using existing RAG system...")
    
    # Use the existing retriever from RAG system
    retriever = rag_system.retriever
    
    # Create empathy-focused prompt
    EMPATHY_RAG_PROMPT = """\
Given a provided context and question, you must answer the question based only on context.

If you cannot answer the question based on the context - you must say "I don't know".

You must answer the question using empathy and kindness, and make sure the user feels heard.

Context: {context}
Question: {question}
"""
    empathy_rag_prompt = ChatPromptTemplate.from_template(EMPATHY_RAG_PROMPT)
    
    # Create LLM using Ollama
    llm = Ollama(model="qwen:latest")
    
    # Create improved RAG chain
    empathy_rag_chain = (
        {"context": itemgetter("question") | retriever, "question": itemgetter("question")}
        | empathy_rag_prompt | llm | StrOutputParser()
    )
    
    return empathy_rag_chain

# ============================================================================
# Evaluation Setup
# ============================================================================

def setup_evaluators():
    """Set up evaluation components using Ollama"""
    from langchain_community.llms import Ollama
    from ragas.metrics import (
        answer_relevancy,
        faithfulness,
        context_recall,
        context_precision
    )
    
    eval_llm = Ollama(model="qwen:latest")
    
    # RAGAS evaluators
    evaluators = [
        answer_relevancy,
        faithfulness,
        context_recall,
        context_precision
    ]
    
    return evaluators

def evaluate_rag_chain(rag_chain, dataset, evaluators):
    """Evaluate RAG chain using RAGAS"""
    from ragas import evaluate
    from langchain_community.llms import Ollama
    
    print("Evaluating RAG chain with RAGAS...")
    result = evaluate(
        rag_chain,
        dataset,
        evaluators
    )
    return result

# ============================================================================
# LangSmith Integration
# ============================================================================

def create_langsmith_dataset(dataset, dataset_name="NPTE Evaluation Data"):
    """Create LangSmith dataset from RAGAS dataset"""
    from langsmith import Client
    
    client = Client()
    
    print(f"Creating LangSmith dataset: {dataset_name}")
    langsmith_dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="NPTE Evaluation Data"
    )
    
    # Add examples to dataset
    for data_row in dataset.to_pandas().iterrows():
        client.create_example(
            inputs={"question": data_row[1]["question"]},
            outputs={"answer": data_row[1]["answer"]},
            metadata={"context": data_row[1]["contexts"]},
            dataset_id=langsmith_dataset.id
        )
    
    print(f"Added {len(dataset.to_pandas())} examples to dataset")
    return langsmith_dataset

# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Main execution function"""
    print("=" * 60)
    print("EVALUATING AGENTS WITH RAGAS")
    print("=" * 60)
    
    # Check if Ollama is available
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            available_models = [model["name"] for model in models]
            print(f"✅ Ollama is running. Available models: {available_models}")
            
            required_models = ["qwen:latest", "nomic-embed-text:latest"]
            missing_models = [model for model in required_models if model not in available_models]
            
            if missing_models:
                print(f"⚠️ Missing required models: {missing_models}")
                print("Please install missing models with: ollama pull <model_name>")
                return
            else:
                print("✅ All required models are available")
        else:
            print("❌ Ollama is not responding properly")
            return
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {e}")
        print("Please make sure Ollama is running on localhost:11434")
        return
    
    # Step 1: Load documents and RAG system
    print("\n1. Loading documents and RAG system...")
    rag_system = load_documents()
    
    # Verify we're using existing embeddings
    print(f"✅ Using existing Qdrant collection: {rag_system.collection_name}")
    print(f"✅ Using existing embeddings model: nomic-embed-text:latest")
    print(f"✅ Vector store path: ../backend/qdrant_data")
    
    # Step 2: Set up RAGAS components
    print("\n2. Setting up RAGAS components...")
    generator_llm, generator_embeddings = setup_ragas_components()
    
    # Step 3: Retrieve documents from existing vector store
    print("\n3. Retrieving documents from existing vector store...")
    docs = rag_system.retrieve_relevant_context("therapy", k=20)
    print(f"Retrieved {len(docs)} documents from existing vector store")
    
    if len(docs) == 0:
        print("❌ No documents found in vector store. Please ensure documents are loaded.")
        print("💡 Try running: cd ../backend && python check_qdrant.py")
        return
    
    print(f"✅ Successfully using existing embeddings with {len(docs)} documents")
    
    # Save documents to JSON file for inspection
    import json
    docs_as_dicts = [{"content": doc.page_content, "metadata": doc.metadata} for doc in docs]
    
    with open("docs_dump.json", "w") as f:
        json.dump(docs_as_dicts, f, indent=2)
    print(f"✅ Saved {len(docs)} documents to docs_dump.json")
    
    # Exit here to inspect the documents
   # print("🛑 Exiting to allow inspection of documents...")
   # import sys
   # sys.exit(0) 
    # Step 4: Create knowledge graph
    print("\n4. Creating knowledge graph...")
    kg = create_knowledge_graph(docs, generator_llm, generator_embeddings)
    
    # Step 5: Apply transformations (skipping for now due to performance issues)
    print("\n5. Skipping transformations (performance optimization)...")
    # kg = apply_transformations(kg, docs, generator_llm, generator_embeddings)
    print("✅ Knowledge graph ready for synthetic data generation")
    
    # Step 6: Generate synthetic data
    print("\n6. Generating synthetic data...")
    dataset = generate_synthetic_data(docs, generator_llm, generator_embeddings, testset_size=2)
    print(f"✅ Generated {len(dataset.to_pandas())} synthetic test examples")
    
    # Step 7: Create LangSmith dataset
    print("\n7. Creating LangSmith dataset...")
    dataset_name = "NPTE Evaluation Data"
    langsmith_dataset = create_langsmith_dataset(dataset, dataset_name)
    
    # Step 8: Set up RAG chains
    print("\n8. Setting up RAG chains...")
    basic_rag_chain = setup_basic_rag_chain(rag_system)
    improved_rag_chain = setup_improved_rag_chain(rag_system)
    
    # Step 9: Set up evaluators
    print("\n9. Setting up evaluators...")
    evaluators = setup_evaluators()
    
    # Step 10: Evaluate basic chain
    print("\n10. Evaluating basic RAG chain...")
    basic_results = evaluate_rag_chain(basic_rag_chain, dataset, evaluators)
    
    # Step 11: Evaluate improved chain
    print("\n11. Evaluating improved RAG chain...")
    improved_results = evaluate_rag_chain(improved_rag_chain, dataset, evaluators)
    
    # Step 12: Display results
    print("\n" + "=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)
    print("Basic RAG Chain Results:")
    print(basic_results)
    print("\nImproved RAG Chain Results:")
    print(improved_results)
    
    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)
    print("Check LangSmith for detailed results:")
    print(f"Dataset: {dataset_name}")
    print(f"Basic chain: {basic_results}")
    print(f"Improved chain: {improved_results}")

if __name__ == "__main__":
    main() 