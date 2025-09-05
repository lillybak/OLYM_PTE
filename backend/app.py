"""
FastAPI Backend Integration for FIXED LangGraph NPTE System
Addresses all 4 identified issues
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from dotenv import load_dotenv
import traceback
import uuid

# Import the FIXED LangGraph agent
from npte_langgraph_fixed import NPTEProfessorAgent

load_dotenv()

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class PromptRequest(BaseModel):
    prompt: str

class MCQResponse(BaseModel):
    question: str
    choices: List[str]
    correct: int
    explanations: Dict[str, str]  # Changed to string keys for compatibility
    links: Dict[str, List[str]]
    session_id: str  # Add session ID for frontend tracking

class AnswerRequest(BaseModel):
    session_id: str
    user_answer_index: int

class EvaluationResponse(BaseModel):
    is_correct: bool
    explanation: str
    study_links: List[str]
    study_message: Optional[str] = ""
    continue_available: bool
    topic_selection_available: bool
    continue_message: Optional[str] = ""

class ContinueRequest(BaseModel):
    session_id: str

# Global agent instance
professor_agent = None

@app.on_event("startup")
async def startup_event():
    """Initialize the FIXED NPTE Professor Agent on startup"""
    global professor_agent
    try:
        professor_agent = NPTEProfessorAgent()
        print("✅ FIXED NPTE Professor Agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        professor_agent = None

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "message": "NPTE LangGraph System (FIXED) is running!",
        "agent_status": "available" if professor_agent else "unavailable",
        "version": "fixed_v1.0"
    }

@app.post("/api/ask", response_model=MCQResponse)
async def generate_question(request: PromptRequest):
    """
    FIXED: Generate MCQ with topic-focused links and proper explanations
    Addresses Issue #1 (unrelated links) and Issue #3 (explanation format)
    """
    global professor_agent
    
    if professor_agent is None:
        raise HTTPException(status_code=503, detail="Professor agent not initialized")
    
    try:
        topic = request.prompt.strip()
        session_id = str(uuid.uuid4())  # Generate unique session ID
        
        print(f"🎓 Generating NPTE question for topic: {topic}")
        
        # Use the FIXED agent
        mcq_data = await professor_agent.generate_mcq(topic, session_id)
        
        # Convert to string keys for frontend compatibility
        explanations_str = {str(k): str(v) for k, v in mcq_data.get("explanations", {}).items()}
        links_str = {str(k): v for k, v in mcq_data.get("links", {}).items()}
        
        response = MCQResponse(
            question=mcq_data["question"],
            choices=mcq_data["choices"],
            correct=mcq_data["correct"],
            explanations=explanations_str,
            links=links_str,
            session_id=session_id
        )
        
        # Store session ID for evaluation (you might want to use Redis in production)
        # For now, we'll rely on the agent's internal caching
        
        print(f"✅ Generated question with session ID: {session_id}")
        return response
        
    except Exception as e:
        print(f"❌ Question generation failed: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate question for {request.prompt}: {e}"
        )

@app.post("/api/evaluate", response_model=EvaluationResponse)
async def evaluate_answer(request: AnswerRequest):
    """
    NEW ENDPOINT - FIXED: Evaluate user's answer with comprehensive explanations
    Addresses Issue #3 (explanation format) and Issue #4 (button availability)
    """
    global professor_agent
    
    if professor_agent is None:
        raise HTTPException(status_code=503, detail="Professor agent not initialized")
    
    try:
        print(f"📊 Evaluating answer for session {request.session_id}")
        print(f"📊 User answer index: {request.user_answer_index}")
        print(f"📊 Request: {request}")
        
        # Use the FIXED agent evaluation
        eval_result = await professor_agent.evaluate_answer(
            request.session_id, 
            request.user_answer_index
        )
        
        response = EvaluationResponse(
            is_correct=eval_result["is_correct"],
            explanation=eval_result["explanation"],
            study_links=eval_result["study_links"],
            continue_available=eval_result["continue_available"],
            topic_selection_available=eval_result["topic_selection_available"],
            continue_message=eval_result.get("continue_message", "")
        )
        
        print(f"✅ Evaluation completed: {'Correct' if response.is_correct else 'Incorrect'}")
        return response
        
    except Exception as e:
        print(f"❌ Answer evaluation failed: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to evaluate answer: {e}"
        )

@app.post("/api/continue", response_model=MCQResponse)
async def continue_same_topic(request: ContinueRequest):
    """
    FIXED: Continue with same topic - generate new question
    Addresses Issue #4 (continue functionality)
    """
    global professor_agent
    
    if professor_agent is None:
        raise HTTPException(status_code=503, detail="Professor agent not initialized")
    
    try:
        print(f"🔄 Continuing same topic for session {request.session_id}")
        
        # Use the FIXED agent continue functionality
        mcq_data = await professor_agent.continue_same_topic(request.session_id)
        
        if "error" in mcq_data:
            raise HTTPException(status_code=400, detail=mcq_data["error"])
        
        # Convert to string keys for frontend compatibility
        explanations_str = {str(k): str(v) for k, v in mcq_data.get("explanations", {}).items()}
        links_str = {str(k): v for k, v in mcq_data.get("links", {}).items()}
        
        response = MCQResponse(
            question=mcq_data["question"],
            choices=mcq_data["choices"],
            correct=mcq_data["correct"],
            explanations=explanations_str,
            links=links_str
        )
        
        print(f"✅ Generated continue question")
        return response
        
    except Exception as e:
        print(f"❌ Continue same topic failed: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to continue same topic: {e}"
        )

@app.get("/api/random")
def get_random():
    """Legacy endpoint for compatibility"""
    from random import randint
    return {"number": randint(1, 100)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
