"""
NPTE Agent System with Tool-Belt Architecture
Agent with RAG tool (Qdrant embeddings) + Web tool (Tavily) + Cohere tools
"""

import os
import json
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import openai
from rag_system import get_rag_context, initialize_rag_system

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

# ============================================================================
# PLACEHOLDER: Cohere imports
# import cohere
# co = cohere.Client(os.getenv("COHERE_API_KEY"))
# ============================================================================

# ============================================================================
# PLACEHOLDER: LangSmith tracing
# from langsmith import trace
# import os
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
# os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
# os.environ["LANGCHAIN_PROJECT"] = "npte-mcq-agent"
# ============================================================================

class NPTEAgent:
    """Agent with tool-belt for NPTE MCQ generation"""
    
    def __init__(self):
        self.rag_system = initialize_rag_system()
        self.conversation_history = []
        
        # ============================================================================
        # PLACEHOLDER: Initialize Cohere tools
        # self.cohere_client = co
        # ============================================================================
        
    def generate_mcq(self, topic: str) -> Dict[str, Any]:
        """Generate MCQ using agent's tool-belt with multiple retrieval options"""
        
        # ============================================================================
        # PLACEHOLDER: LangSmith tracing
        # @trace(name="generate_mcq")
        # def traced_generate_mcq(topic: str):
        #     return self._generate_mcq_internal(topic)
        # return traced_generate_mcq(topic)
        # ============================================================================
        
        return self._generate_mcq_internal(topic)
    
    def _generate_mcq_internal(self, topic: str) -> Dict[str, Any]:
        """Internal MCQ generation with tracing"""
        
        # Agent decides which retrieval method to use
        retrieval_method = self._choose_retrieval_method(topic)
        
        if retrieval_method == "cohere":
            context = self._get_cohere_context(topic)
        elif retrieval_method == "rag":
            context = self._get_rag_context(topic)
        elif retrieval_method == "hybrid":
            context = self._get_hybrid_context(topic)
        else:
            context = self._get_general_context(topic)
        
        # Simulate web search (you'll integrate Tavily later)
        web_context = self._simulate_web_search(topic)
        
        # Combine contexts
        combined_context = self._combine_contexts(context, web_context)
        
        # Generate MCQ using LLM
        mcq = self._generate_with_llm(topic, combined_context)
        
        return mcq
    
    def _choose_retrieval_method(self, topic: str) -> str:
        """Agent decides which retrieval method to use"""
        
        # For now, use RAG for all topics since we don't have data to influence the choice
        # You can add logic later when you have performance data
        return "rag"
    
    def _get_cohere_context(self, topic: str) -> str:
        """Get context using Cohere retriever"""
        # ============================================================================
        # PLACEHOLDER: Cohere retrieval with tracing
        # @trace(name="cohere_retrieval")
        # def traced_cohere_retrieval(topic: str):
        #     try:
        #         response = self.cohere_client.search(
        #             query=f"NPTE {topic} multiple choice questions",
        #             documents=your_documents,  # Your PDF chunks
        #             model="rerank-english-v2.0",
        #             top_n=5
        #         )
        #         return "\n".join([doc.text for doc in response.results])
        #     except Exception as e:
        #         print(f"Cohere retrieval failed: {e}")
        #         return ""
        # return traced_cohere_retrieval(topic)
        # ============================================================================
        
        # Placeholder for now
        return f"Cohere retrieved context for {topic}: Advanced retrieval with reranking."
    
    def _get_rag_context(self, topic: str) -> str:
        """Get context using RAG system"""
        # ============================================================================
        # PLACEHOLDER: RAG retrieval with tracing
        # @trace(name="rag_retrieval")
        # def traced_rag_retrieval(topic: str):
        #     try:
        #         return get_rag_context(topic)
        #     except Exception as e:
        #         print(f"RAG retrieval failed: {e}")
        #         return ""
        # return traced_rag_retrieval(topic)
        # ============================================================================
        
        try:
            return get_rag_context(topic)
        except Exception as e:
            print(f"RAG retrieval failed: {e}")
            return ""
    
    def _get_hybrid_context(self, topic: str) -> str:
        """Get context using both Cohere and RAG"""
        cohere_context = self._get_cohere_context(topic)
        rag_context = self._get_rag_context(topic)
        
        if cohere_context and rag_context:
            return f"Cohere Results:\n{cohere_context}\n\nRAG Results:\n{rag_context}"
        elif cohere_context:
            return cohere_context
        elif rag_context:
            return rag_context
        else:
            return ""
    
    def _get_general_context(self, topic: str) -> str:
        """Get context using general knowledge only"""
        return f"General PT knowledge about {topic}"
    
    def _simulate_web_search(self, topic: str) -> str:
        """Simulate web search (replace with Tavily integration)"""
        # Placeholder for web search
        return f"Current medical literature on {topic}: Latest protocols and guidelines."
    
    def _combine_contexts(self, retrieval_context: str, web_context: str) -> str:
        """Combine retrieval and web contexts"""
        if retrieval_context and web_context:
            return f"Retrieved Knowledge:\n{retrieval_context}\n\nCurrent Literature:\n{web_context}"
        elif retrieval_context:
            return f"Retrieved Knowledge:\n{retrieval_context}"
        elif web_context:
            return web_context
        else:
            return "General PT knowledge"
    
    def _generate_with_llm(self, topic: str, context: str) -> Dict[str, Any]:
        """Generate MCQ using LLM"""
        
        # ============================================================================
        # PLACEHOLDER: LLM generation with tracing
        # @trace(name="llm_generation")
        # def traced_llm_generation(topic: str, context: str):
        #     return self._generate_with_llm_internal(topic, context)
        # return traced_llm_generation(topic, context)
        # ============================================================================
        
        return self._generate_with_llm_internal(topic, context)
    
    def _generate_with_llm_internal(self, topic: str, context: str) -> Dict[str, Any]:
        """Internal LLM generation with tracing"""
        
        system_prompt = (
            "You are an expert NPTE-PT exam tutor. Generate NPTE-style multiple-choice questions with clinical scenarios. "
            "Use the provided context to create accurate, relevant questions. "
            "Return ONLY a JSON object with this exact format: {\"question\": \"Clinical scenario with question?\", "
            "\"choices\": [\"A. First choice\", \"B. Second choice\", \"C. Third choice\", \"D. Fourth choice\"], \"correct\": 2, "
            "\"explanations\": {0: \"Why A is wrong\", 1: \"Why B is wrong\", 2: \"Why C is correct\", 3: \"Why D is wrong\"}, "
            "\"links\": {0: [\"https://...\"], 1: [\"https://...\"], 2: [\"https://...\"], 3: [\"https://...\"]}}. "
            "Use A, B, C, D format for choices. 'correct' is 0-based index (0=A, 1=B, 2=C, 3=D). "
            "Explanations should be detailed clinical reasoning. Links should be relevant medical resources."
        )
        
        user_prompt = f"Topic: {topic}\n\nContext:\n{context}\n\nGenerate an MCQ as described."
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=800,
                temperature=0.7,
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    mcq_data = json.loads(json_str)
                    
                    question = mcq_data.get("question", "")
                    choices = mcq_data.get("choices", [])
                    correct = mcq_data.get("correct", 0)
                    explanations = mcq_data.get("explanations", {})
                    links = mcq_data.get("links", {})
                    
                    if isinstance(choices, list) and len(choices) == 4:
                        return {
                            "question": question,
                            "choices": choices,
                            "correct": correct,
                            "explanations": explanations,
                            "links": links
                        }
            except Exception as e:
                print(f"JSON parsing failed: {e}")
                
        except Exception as e:
            print(f"LLM call failed: {e}")
        
        # Fallback
        return self._get_fallback_mcq(topic)
    
    def _get_fallback_mcq(self, topic: str) -> Dict[str, Any]:
        """Fallback MCQ when LLM fails"""
        return {
            "question": f"A patient presents with symptoms related to {topic}. Which of the following is the MOST likely diagnosis?",
            "choices": [
                "A. Option A",
                "B. Option B", 
                "C. Option C",
                "D. Option D"
            ],
            "correct": 2,
            "explanations": {
                0: "Option A is incorrect because...",
                1: "Option B is incorrect because...",
                2: "Option C is correct because...",
                3: "Option D is incorrect because..."
            },
            "links": {
                0: ["https://www.ncbi.nlm.nih.gov/"],
                1: ["https://www.ncbi.nlm.nih.gov/"],
                2: ["https://www.ncbi.nlm.nih.gov/"],
                3: ["https://www.ncbi.nlm.nih.gov/"]
            }
        }
    
    def validate_answer(self, topic: str, selected_answer: int, correct_answer: int, explanations: dict) -> Dict[str, Any]:
        """Validate student's answer and provide feedback"""
        
        # ============================================================================
        # PLACEHOLDER: Answer validation with tracing
        # @trace(name="validate_answer")
        # def traced_validate_answer(topic: str, selected_answer: int, correct_answer: int, explanations: dict):
        #     return self._validate_answer_internal(topic, selected_answer, correct_answer, explanations)
        # return traced_validate_answer(topic, selected_answer, correct_answer, explanations)
        # ============================================================================
        
        return self._validate_answer_internal(topic, selected_answer, correct_answer, explanations)
    
    def _validate_answer_internal(self, topic: str, selected_answer: int, correct_answer: int, explanations: dict) -> Dict[str, Any]:
        """Internal answer validation with tracing"""
        
        system_prompt = (
            "You are an expert NPTE-PT exam tutor. Evaluate the user's answer and provide detailed feedback. "
            "Consider the user's mastery level and suggest whether they should continue with the same topic."
        )
        
        user_prompt = f"""
        Topic: {topic}
        User selected: {selected_answer}
        Correct answer: {correct_answer}
        Explanation for selected answer: {explanations.get(selected_answer, 'No explanation available')}
        
        Provide feedback and suggest next steps.
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=300,
                temperature=0.3,
            )
            
            content = response.choices[0].message.content.strip()
            is_correct = selected_answer == correct_answer
            
            return {
                "correct": is_correct,
                "explanation": content,
                "suggest_same_topic": not is_correct,
                "mastery_level": 0.5  # Placeholder
            }
            
        except Exception as e:
            print(f"Answer validation failed: {e}")
            return {
                "correct": selected_answer == correct_answer,
                "explanation": "Unable to provide detailed feedback at this time.",
                "suggest_same_topic": selected_answer != correct_answer,
                "mastery_level": 0.5
            }

# Global agent instance
agent = None

def get_agent():
    """Get or create the global agent instance"""
    global agent
    if agent is None:
        agent = NPTEAgent()
    return agent 