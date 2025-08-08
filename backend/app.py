import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from random import randint
import openai
from dotenv import load_dotenv
import json
import re
import traceback
from typing import Dict, List, Optional

# Import agent system
from ollama_agent import get_ollama_agent
from fastapi import HTTPException

load_dotenv()  # Load .env file
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()  # New OpenAI client for v1.0.0+

app = FastAPI()

# Allow frontend (React) to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# PLACEHOLDER: Future LangChain/LangGraph imports
# from langchain import LLMChain, PromptTemplate
# from langgraph import StateGraph, END
# from langsmith import trace
# ============================================================================

# ============================================================================
# PLACEHOLDER: Future evaluation components
# import ragas
# from ragas import evaluate
# ============================================================================

class PromptRequest(BaseModel):
    prompt: str

class MCQResponse(BaseModel):
    question: str
    choices: list[str]
    correct: int
    explanations: dict
    links: dict

# Removed AnswerRequest and AnswerValidationResponse classes - no longer needed

class DocumentUploadResponse(BaseModel):
    message: str
    documents_processed: int
    chunks_created: int

# ============================================================================
# PLACEHOLDER: User progress tracking for adaptive learning
user_progress: Dict[str, Dict] = {}  # topic -> {correct_count, total_count, mastery_level}
# ============================================================================

# Initialize agent
agent = None

@app.on_event("startup")
async def startup_event():
    """Initialize agent and RAG system on startup"""
    global agent
    try:
        # Initialize Ollama agent
        agent = get_ollama_agent()
        print("✅ Ollama agent system initialized successfully")
        
        # TODO: Initialize RAG system and load documents
        # from rag_system import NPTERAGSystem
        # rag_system = NPTERAGSystem()
        # rag_system.load_documents_from_directory("../data/")
        # print("✅ RAG system initialized with documents")
        
    except Exception as e:
        print(f"⚠️ System initialization failed: {e}")
        agent = None

@app.post("/api/ask", response_model=MCQResponse)
async def ask(request: PromptRequest):
    """Generate MCQ using agent with tool-belt"""
    global agent
    
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent system not initialized")
    
    try:
        mcq_data = agent.generate_mcq(request.prompt)
        return MCQResponse(**mcq_data)
    except Exception as e:
        print(f"Ollama MCQ generation failed: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate MCQ for {request.prompt}: {e}")

# Removed /api/validate_answer endpoint - validation now handled client-side

@app.post("/api/upload_documents", response_model=DocumentUploadResponse)
async def upload_documents():
    """Upload and process documents for RAG"""
    try:
        # This will be handled by the agent's RAG system
        return DocumentUploadResponse(
            message="Documents processed by agent RAG system",
            documents_processed=1,
            chunks_created=1
        )
        
    except Exception as e:
        print(f"Document upload failed: {e}")
        return DocumentUploadResponse(
            message=f"Document processing failed: {str(e)}",
            documents_processed=0,
            chunks_created=0
        )

# ============================================================================
# PLACEHOLDER: Future endpoints for evaluation, etc.
# @app.post("/api/evaluate_system")
# async def evaluate_system():
#     """Run RAGAS evaluation."""
#     pass
# ============================================================================

@app.get("/")
def read_root():
    return {"message": "FastAPI backend is running!"}

@app.get("/api/random")
def get_random():
    return {"number": randint(1, 100)}
