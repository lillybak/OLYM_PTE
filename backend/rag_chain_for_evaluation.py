#!/usr/bin/env python3
"""
RAG Chain for RAGAS Evaluation
This creates a RAG chain that matches the existing system architecture
"""

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain.schema import StrOutputParser
from operator import itemgetter
from rag_system import NPTERAGSystem

def create_rag_chain_for_evaluation():
    """Create a RAG chain that matches the existing system for RAGAS evaluation"""
    
    # Initialize the RAG system (same as in your notebook)
    rag_system = NPTERAGSystem()
    rag_system.setup_collection()
    
    # Use the existing retriever from RAG system
    retriever = rag_system.retriever
    
    # Create a prompt that matches your system's style
    RAG_PROMPT = """\
You are an NPTE-PT exam tutor assistant. Answer the question based ONLY on the provided context.

If you cannot answer the question based on the context, say "I don't have enough information to answer this question."

Context: {context}
Question: {question}

Answer:"""

    rag_prompt = ChatPromptTemplate.from_template(RAG_PROMPT)
    
    # Create LLM using the same model as your system
    llm = ChatOpenAI(model="gpt-4o-mini")
    
    # Create RAG chain
    rag_chain = (
        {"context": itemgetter("question") | retriever, "question": itemgetter("question")}
        | rag_prompt | llm | StrOutputParser()
    )
    
    return rag_chain

def create_rag_chain_with_ollama():
    """Create a RAG chain using Ollama (matching your existing system)"""
    
    # Initialize the RAG system
    rag_system = NPTERAGSystem()
    rag_system.setup_collection()
    
    # Use the existing retriever from RAG system
    retriever = rag_system.retriever
    
    # Create a prompt that matches your system's style
    RAG_PROMPT = """\
You are an NPTE-PT exam tutor assistant. Answer the question based ONLY on the provided context.

If you cannot answer the question based on the context, say "I don't have enough information to answer this question."

Context: {context}
Question: {question}

Answer:"""

    rag_prompt = ChatPromptTemplate.from_template(RAG_PROMPT)
    
    # Create LLM using Ollama (same as your existing system)
    from langchain_community.llms import Ollama
    llm = Ollama(model="qwen:latest")
    
    # Create RAG chain
    rag_chain = (
        {"context": itemgetter("question") | retriever, "question": itemgetter("question")}
        | rag_prompt | llm | StrOutputParser()
    )
    
    return rag_chain

if __name__ == "__main__":
    print("Testing RAG chain for evaluation...")
    
    # Test with OpenAI
    print("Creating RAG chain with OpenAI...")
    rag_chain_openai = create_rag_chain_for_evaluation()
    
    # Test with Ollama
    print("Creating RAG chain with Ollama...")
    rag_chain_ollama = create_rag_chain_with_ollama()
    
    print("✅ RAG chains ready for RAGAS evaluation!")
