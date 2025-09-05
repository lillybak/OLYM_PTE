"""
NPTE Expert Professor Agent - LangGraph Implementation (FIXED VERSION)
Clean implementation addressing all identified issues
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, TypedDict, Annotated
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

# LLM Setup - OpenAI GPT-4o-mini
OPENAI_AVAILABLE = False
# Updated to use OpenAI GPT-4o-mini for optimal performance
LLM_MODEL = "gpt-4o-mini"  # OpenAI GPT-4o-mini

try:
    print("🔍 DIAGNOSTIC: Starting OpenAI setup...")
    from langchain_openai import ChatOpenAI
    print("✅ DIAGNOSTIC: ChatOpenAI import successful")
    
    api = os.getenv("OPENAI_API_KEY")
    print(f"🔍 DIAGNOSTIC: API key length: {len(api) if api else 0}")
    print(f"🔍 DIAGNOSTIC: API key starts with: {api[:10] if api else 'None'}...")
    
    if api and len(api.strip()) > 10:
        # Configure OpenAI with optimized parameters
        llm = ChatOpenAI(
            model=LLM_MODEL, 
            temperature=0.2,
            max_tokens=2048,  # Reasonable limit for NPTE responses
            top_p=0.95,       # Good balance of creativity and consistency
            seed=None  # Remove seed for variety
        )
        print("🔍 DIAGNOSTIC: Testing LLM connection...")
        # Test the LLM connection with a real question
        test_response = llm.invoke("What is 2+2? Answer with just the number.")
        print(f"🔍 DIAGNOSTIC: Test response type: {type(test_response)}")
        print(f"🔍 DIAGNOSTIC: Test response: {test_response}")
        
        if test_response and hasattr(test_response, 'content') and test_response.content.strip():
            response_content = test_response.content.strip()
            # Check if we got a real response (not an error message)
            if len(response_content) > 0 and not any(error_word in response_content.lower() for error_word in ['error', 'failed', 'unavailable', 'mock']):
                OPENAI_AVAILABLE = True
                print(f"✅ OpenAI LLM initialized successfully!")
                print(f"✅ Model: {LLM_MODEL}")
                print(f"✅ Temperature: 0.2, Seed: 42")
                print(f"✅ API Key length: {len(api)} characters (valid OpenAI key format)")
                print(f"✅ Test response: '{response_content}'")
            else:
                OPENAI_AVAILABLE = False
                print(f"❌ OpenAI LLM test failed - got error response: '{response_content}'")
        else:
            OPENAI_AVAILABLE = False
            print("❌ OpenAI LLM test failed - no valid response")
    else:
        print("❌ DIAGNOSTIC: OPENAI_API_KEY missing or too short")
        print(f"❌ DIAGNOSTIC: API key value: {api}")
except Exception as e:
    print(f"❌ DIAGNOSTIC: OpenAI setup failed: {e}")
    import traceback
    print(f"❌ DIAGNOSTIC: Full error traceback:")
    traceback.print_exc()

# Tavily setup
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True if os.getenv("TAVILY_API_KEY") else False
except ImportError:
    TAVILY_AVAILABLE = False

print(f"🔧 Setup: OpenAI={OPENAI_AVAILABLE}, Tavily={TAVILY_AVAILABLE}")

# ============================================================================
# STATE DEFINITION
# ============================================================================

class NPTEState(TypedDict):
    """Simplified state for NPTE learning system"""
    topic: str
    question: Optional[str]
    choices: Optional[List[str]]
    correct_answer_index: Optional[int]
    user_answer_index: Optional[int]
    is_correct: Optional[bool]
    explanation: Optional[str]
    study_links: Optional[List[str]]
    continue_topic: Optional[bool]
    error: Optional[str]
    # New fields for better explanation handling
    choice_explanations: Optional[Dict[str, str]]  # Individual choice explanations
    continue_available: Optional[bool]  # Whether continue button should show
    topic_selection_available: Optional[bool]  # Whether topic selection should be available

# ============================================================================
# PROFESSOR'S FOCUSED TOOLS
# ============================================================================

@tool
async def query_pdf_knowledge(topic: str, query: str = "", choice_content: str = "") -> Dict:
    """
    Query PDF knowledge from existing Qdrant embeddings for choice-specific content
    Uses your pre-built RAG system with PDF embeddings
    """
    try:
        # Import your existing RAG system
        import sys
        sys.path.append('/home/olb/demo2025/demo-OLYM_PTE/backend')
        from rag_system import initialize_rag_system
        
        # Initialize RAG system with OpenAI embeddings (1536 dimensions)
        from rag_system import NPTERAGSystem
        
        # Create RAG system with your collection name (rag_system.py now uses OpenAI embeddings)
        rag_system = NPTERAGSystem(collection_name="npte_materials_v2")
        rag_system.setup_collection()
        
        # FIXED: Create choice-specific search query
        if choice_content:
            # Search specifically for the choice content within the topic context
            search_query = f"{topic} {choice_content} {query}".strip()
            print(f"📚 Querying PDF knowledge for choice: {choice_content} in {topic}")
        else:
            # Fallback to general topic search
            search_query = f"{topic} {query}" if query else topic
            print(f"📚 Querying PDF knowledge for: {topic}")
        
        # Get relevant documents from your Qdrant embeddings
        docs = rag_system.retriever.get_relevant_documents(search_query, k=5)
        
        # FIXED: Enhanced PDF source formatting with choice-specific details
        pdf_knowledge = []
        pdf_sources = set()  # Track unique PDF sources
        
        for i, doc in enumerate(docs):
            # Extract PDF source information
            metadata = doc.metadata
            pdf_source = metadata.get('source', 'Unknown PDF')
            page_info = metadata.get('page', 'Unknown page')
            
            # Enhanced content with source attribution
            pdf_knowledge.append({
                "content": doc.page_content,
                "metadata": metadata,
                "pdf_source": pdf_source,
                "page_info": page_info,
                "relevance_rank": i + 1,
                "search_context": choice_content if choice_content else topic,
                "source_type": "pdf_embeddings"
            })
            
            # Track unique sources
            pdf_sources.add(pdf_source)
        
        # Create source summary
        source_summary = list(pdf_sources)
        
        print(f"✅ Found {len(pdf_knowledge)} relevant PDF chunks from {len(source_summary)} PDFs")
        if choice_content:
            print(f"📄 Choice-specific content found in: {source_summary[:3]}")  # Show first 3 sources
        
        return {
            "status": "success",
            "topic": topic,
            "choice_content": choice_content,
            "pdf_chunks": pdf_knowledge,
            "pdf_sources": source_summary,
            "total_found": len(docs),
            "unique_sources": len(source_summary)
        }
        
    except Exception as e:
        print(f"⚠️ PDF knowledge query failed: {e}")
        return {
            "status": "error",
            "message": f"Failed to query PDF knowledge: {e}",
            "pdf_chunks": []
        }

@tool
async def get_topic_focused_links(topic: str, is_correct: bool = False, choice_content: str = "", question_text: str = "", all_choices: List[str] = None) -> List[str]:
    """
    CONTEXTUAL: Get relevant learning links using keywords from actual question/choices
    No hardcoded terms - extracts context from the specific MCQ content
    """
    try:
        # EXTRACT contextual keywords from the actual question and choices (not hardcoded)
        all_choices = all_choices or []
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", 
                     "should", "would", "could", "will", "most", "best", "appropriate", "likely", "patient", "following"}
        
        # Extract keywords from question
        question_keywords = []
        if question_text:
            question_keywords = [word for word in question_text.lower().split() 
                               if len(word) > 3 and word not in stop_words and word.isalpha()]
        
        # Extract keywords from all choices to understand the clinical context
        choice_keywords = []
        for choice in all_choices:
            clean_choice = choice.replace('A. ', '').replace('B. ', '').replace('C. ', '').replace('D. ', '')
            choice_keywords.extend([word for word in clean_choice.lower().split() 
                                  if len(word) > 3 and word not in stop_words and word.isalpha()])
        
        # Combine and deduplicate - these are the ACTUAL terms from this specific MCQ
        contextual_keywords = list(set(question_keywords + choice_keywords))
        print(f"🔍 Using contextual keywords from this MCQ: {contextual_keywords[:6]}")
        
        if not TAVILY_AVAILABLE:
            return [
                f"https://physiopedia.com/search?q={topic.replace(' ', '+')}", 
                f"https://www.apta.org/search?q={topic.replace(' ', '+')}"
            ]
        
        tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        
        # ENHANCED: More flexible search for both correct and incorrect answers
        if choice_content:
            # Use the actual choice content for targeted search - NO "NPTE" to avoid test prep sites
            if is_correct:
                # For correct answers: Multiple search approaches to ensure we find content
                search_query = f"{choice_content} {topic} physical therapy technique intervention"
                print(f"🎯 Primary correct search: {search_query}")
            else:
                # For incorrect answers: contraindications and limitations of this intervention
                search_query = f"{choice_content} {topic} contraindications limitations precautions physical therapy when to avoid"
        else:
            # Fallback to general topic search - focus on clinical content
            if is_correct:
                search_query = f"{topic} physical therapy treatment intervention technique"
            else:
                search_query = f"{topic} fundamentals clinical reasoning physical therapy treatment approaches"
        
        print(f"🎯 Focused search: {search_query}")
        
        results = tavily_client.search(
            query=search_query,
            max_results=8,  # More results to find diverse quality sources
            search_depth="advanced"  # Let Tavily find the best sources
        )
        
        print(f"📊 Tavily returned {len(results.get('results', []))} results")
        for i, result in enumerate(results.get("results", [])[:3]):  # Show first 3 for debugging
            print(f"  {i+1}. {result.get('title', 'No title')[:60]}...")
            print(f"     URL: {result.get('url', 'No URL')}")
            print(f"     Content: {result.get('content', 'No content')[:100]}...")
        
        # Extract only URLs that are truly relevant to the topic
        topic_links = []
        topic_keywords = topic.lower().split()
        
        # ENHANCED: Filter for clinical education content, exclude test prep sites
        for result in results.get("results", []):
            url = result.get("url", "")
            title = result.get("title", "").lower()
            content = result.get("content", "").lower()
            
            # EXCLUDE test prep and generic NPTE sites
            test_prep_indicators = ["practice test", "practice exam", "test prep", "exam prep", "mometrix", 
                                  "kaplan", "study guide", "flashcards", "mock exam", "sample questions",
                                  "practice questions", "quiz", "npte prep", "exam review"]
            is_test_prep = any(indicator in title or indicator in url.lower() for indicator in test_prep_indicators)
            
            if is_test_prep:
                print(f"🚫 Excluding test prep site: {title[:50]}...")
                continue
            
            # PRIORITIZE clinical education content
            clinical_education_indicators = ["research", "evidence", "study", "clinical", "journal", "guidelines",
                                           "intervention", "treatment", "technique", "protocol", "effectiveness",
                                           "contraindication", "indication", "systematic review", "meta-analysis"]
            clinical_score = sum(1 for indicator in clinical_education_indicators if indicator in title or indicator in content)
            
            # SIMPLE BUT ACCURATE: Does this content actually discuss the specific intervention?
            is_relevant = False
            relevance_reason = ""
            
            if choice_content:
                # Extract meaningful terms from the choice (ignore common words)
                stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "should", "would", "could"}
                choice_terms = [word for word in choice_content.lower().split() 
                               if len(word) > 3 and word not in stop_words]
                
                # Check if content actually mentions the specific technique/intervention
                mentioned_terms = []
                for term in choice_terms:
                    if term in title or term in content:
                        mentioned_terms.append(term)
                
                # Must mention at least one key term from the choice
                if mentioned_terms:
                    is_relevant = True
                    relevance_reason = f"discusses {mentioned_terms[0]}"
                    print(f"✅ SPECIFIC: {result.get('title', 'No title')[:50]}... (mentions: {mentioned_terms[:2]})")
                else:
                    print(f"❌ NOT SPECIFIC: {result.get('title', 'No title')[:50]}... (no mention of: {choice_terms[:2]})")
            else:
                # Fallback: Use extracted contextual keywords from the actual MCQ
                topic_match = any(keyword in title or keyword in content for keyword in topic_keywords)
                context_match = any(keyword in title or keyword in content for keyword in contextual_keywords)
                
                if topic_match and context_match:
                    is_relevant = True
                    relevance_reason = "contextual relevance from MCQ"
                    print(f"✅ CONTEXTUAL: {result.get('title', 'No title')[:50]}... (topic + MCQ context)")
            
            if is_relevant:
                topic_links.append({
                    "url": url, 
                    "title": result.get("title", ""),
                    "reason": relevance_reason
                })
                print(f"📍 Found relevant content: {result.get('title', 'No title')[:50]}... (reason: {relevance_reason})")
            else:
                print(f"⚠️ NOT RELEVANT: {result.get('title', 'No title')[:50]}...")
        
        # Return URLs (no sorting needed since relevance is binary now)
        final_links = [link["url"] for link in topic_links[:4]]
        
        # FALLBACK: If strict filtering found no links, try more lenient approach
        if len(final_links) == 0:
            print(f"⚠️ Strict filtering found no links, trying fallback approach...")
            fallback_links = []
            for result in results.get("results", []):
                url = result.get("url", "")
                title = result.get("title", "").lower()
                content = result.get("content", "").lower()
                
                # Still exclude test prep but be more lenient on content requirements
                test_prep_indicators = ["practice test", "practice exam", "test prep", "exam prep", "mometrix", 
                                      "kaplan", "study guide", "flashcards", "mock exam", "sample questions",
                                      "practice questions", "quiz", "npte prep", "exam review"]
                is_test_prep = any(indicator in title or indicator in url.lower() for indicator in test_prep_indicators)
                
                if not is_test_prep:
                    # CONTEXTUAL: Use keywords from the actual MCQ instead of hardcoded terms
                    context_match = any(keyword in title or keyword in content for keyword in contextual_keywords)
                    topic_match = any(keyword in title or keyword in content for keyword in topic_keywords)
                    
                    # Check for choice-specific content if provided
                    choice_keywords = choice_content.lower().split() if choice_content else []
                    choice_match = any(keyword in title or keyword in content for keyword in choice_keywords) if choice_content else True
                    
                    # Must have contextual relevance (from the actual MCQ) + topic match OR choice match
                    relevance_needed = context_match and (topic_match or choice_match)
                    
                    if relevance_needed:
                        fallback_links.append(url)
                        print(f"📍 Fallback link: {title[:50]}...")
                        if len(fallback_links) >= 3:  # Get more fallback links for correct answers
                            break
            
            final_links = fallback_links
        
        print(f"✅ Found {len(final_links)} topic-specific links")
        return final_links
        
    except Exception as e:
        print(f"⚠️ Topic-focused link search failed: {e}")
        # Fallback to manual topic-specific URLs
        topic_clean = topic.replace(' ', '+')
        return [
            f"https://physiopedia.com/search?q={topic_clean}",
            f"https://www.apta.org/search?q={topic_clean}"
        ]

def load_few_shot_examples() -> str:
    """Load and format the NPTE practice questions as few-shot examples"""
    try:
        with open("/home/olb/demo2025/demo-OLYM_PTE/GRAPH/Typical_NPTE_PRACTICE_QUESTIONS", "r") as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"⚠️ Could not load NPTE examples: {e}")
        return ""

# ============================================================================
# CORE NODES - SIMPLIFIED AND FOCUSED
# ============================================================================

async def generate_question_node(state: NPTEState, config: RunnableConfig) -> NPTEState:
    """
    FIXED: Generate NPTE question using PDF knowledge + web search + few-shot examples
    """
    try:
        topic = state["topic"]
        
        # FIXED: Skip generation if we already have question data (evaluation mode)
        if state.get("question") and state.get("choices") and state.get("correct_answer_index") is not None:
            print(f"📋 Using existing question for evaluation: {topic}")
            print(f"🔍 DEBUG: user_answer_index preserved = {state.get('user_answer_index')}")
            return state
            
        print(f"🎓 Professor generating question for: {topic}")
        
        if not OPENAI_AVAILABLE:
            print("❌ ERROR: OpenAI GPT-4o-mini is not available!")
            print("❌ Please check:")
            print("   1. OPENAI_API_KEY is set in .env file")
            print("   2. API key is valid and has credits")
            print("   3. Network connection is working")
            state["error"] = "OpenAI GPT-4o-mini is not available. Please check your API key and network connection."
            return state
        
        # STEP 1: Get comprehensive PDF knowledge (CACHED for reuse)
        print(f"📚 Step 1: Querying PDF embeddings for {topic} (comprehensive search)")
        pdf_result = await query_pdf_knowledge.ainvoke({
            "topic": topic,
            "query": f"NPTE clinical scenarios assessment treatment evaluation interventions",
            "choice_content": ""  # Comprehensive search for all content
        })
        
        pdf_context = ""
        if pdf_result.get("status") == "success" and pdf_result.get("pdf_chunks"):
            # Cache ALL PDF results for later reuse
            state["cached_pdf_knowledge"] = pdf_result
            
            pdf_texts = [chunk["content"] for chunk in pdf_result["pdf_chunks"][:3]]
            pdf_context = "\n\n".join(pdf_texts)
            print(f"✅ Got PDF context: {len(pdf_context)} chars (cached {len(pdf_result['pdf_chunks'])} chunks)")
        
        # STEP 2: Get current web information (if available)
        web_context = ""
        if TAVILY_AVAILABLE:
            print(f"🌐 Step 2: Getting current web information for {topic}")
            try:
                web_links = await get_topic_focused_links.ainvoke({
                    "topic": topic, 
                    "is_correct": True,
                    "choice_content": ""  # No specific choice during question generation
                })
                if web_links:
                    web_context = f"Current web resources available for {topic}"
                    print(f"✅ Got web context")
            except Exception as e:
                print(f"⚠️ Web context failed: {e}")
        
        # STEP 3: Load few-shot examples
        few_shot_examples = load_few_shot_examples()
        
        # STEP 4: Create enhanced system prompt with all context
        context_section = ""
        if pdf_context:
            context_section += f"\n\nPDF KNOWLEDGE CONTEXT:\n{pdf_context[:1500]}"  # Limit context length
        if web_context:
            context_section += f"\n\nCURRENT INFORMATION:\n{web_context}"
        
        system_prompt = f"""You are an Expert NPTE Professor. Generate a challenging NPTE-style question STRICTLY about: {topic}

CRITICAL: The question MUST be specifically about {topic}. Do not deviate to general PT concepts.

KNOWLEDGE CONTEXT:{context_section}

Here are ACTUAL NPTE PRACTICE QUESTIONS for reference format:

{few_shot_examples}

Requirements:
- Question must be 100% focused on {topic} topic
- Use the PDF knowledge context to create realistic clinical scenarios
- 4 answer choices with A. B. C. D. format (periods, not parentheses)
- One clearly correct answer based on current evidence
- Realistic distractors that test clinical understanding
- Follow the EXACT format shown in the examples above

Return ONLY valid JSON:
{{
    "question": "question text with clinical scenario if appropriate",
    "choices": ["A. choice 1", "B. choice 2", "C. choice 3", "D. choice 4"],
    "correct": 0,
    "explanations": {{
        "0": "INDIVIDUAL explanation for choice A only",
        "1": "INDIVIDUAL explanation for choice B only", 
        "2": "INDIVIDUAL explanation for choice C only",
        "3": "INDIVIDUAL explanation for choice D only"
    }}
}}

CRITICAL: Each explanation key (0,1,2,3) MUST contain explanation for ONLY that specific choice. Do NOT put all explanations in key "0".
"""

        llm = ChatOpenAI(
            model=LLM_MODEL, 
            temperature=0.2,
            max_tokens=2048,
            top_p=0.95,
            seed=None  # Remove seed for variety
        )
        
        print(f"🤖 Using LLM: {LLM_MODEL} for question generation")
        # Remove the connection test to avoid extra API calls
        print(f"✅ DIAGNOSTIC: Using LLM instance for question generation")
        
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Generate NPTE question about {topic} using the provided PDF knowledge")
        ])
        
        # Parse JSON response
        try:
            content = response.content.strip()
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                question_data = json.loads(json_str)
                
                # FIXED: Validate and fix explanations format
                explanations = question_data.get("explanations", {})
                if len(explanations) != 4 or not all(str(i) in explanations for i in range(4)):
                    print("⚠️ Invalid explanations format, generating fallback...")
                    choices = question_data.get("choices", [])
                    correct_idx = question_data.get("correct", 0)
                    question_data["explanations"] = {
                        str(i): f"{'✅ CORRECT' if i == correct_idx else '❌ INCORRECT'}: {choices[i] if i < len(choices) else f'Choice {i+1}'} - Analysis based on {topic} principles."
                        for i in range(4)
                    }
                    print("✅ Generated fallback explanations for all 4 choices")
                
            else:
                raise ValueError("No JSON found")
        except Exception as e:
            print(f"⚠️ JSON parsing failed: {e}")
            print("❌ ERROR: Failed to parse LLM response")
            state["error"] = f"Failed to parse LLM response for {topic}: {e}"
            return state
        
        # Update state
        state["question"] = question_data["question"]
        state["choices"] = question_data["choices"]
        state["correct_answer_index"] = question_data.get("correct", 0)
        state["choice_explanations"] = question_data.get("explanations", {})
        
        print(f"✅ Generated {topic}-focused question")
        return state
        
    except Exception as e:
        state["error"] = f"Question generation failed: {e}"
        return state

async def evaluate_answer_node(state: NPTEState, config: RunnableConfig) -> NPTEState:
    """
    FIXED: Evaluate answer and provide comprehensive explanations for ALL choices
    """
    try:
        user_answer = state.get("user_answer_index")
        correct_answer = state.get("correct_answer_index")
        topic = state["topic"]
        choices = state.get("choices", [])
        question_text = state.get("question", "")
        
        print(f"🔍 DEBUG: Received state keys: {list(state.keys())}")
        print(f"🔍 DEBUG: user_answer_index from state = {user_answer}")
        
        # Determine correctness
        is_correct = user_answer == correct_answer
        state["is_correct"] = is_correct
        
        print(f"🔍 Evaluating: User={user_answer}, Correct={correct_answer}, Result={'✅' if is_correct else '❌'}")
        
        if not OPENAI_AVAILABLE:
            print("❌ ERROR: OpenAI GPT-4o-mini is not available!")
            print("❌ Please check:")
            print("   1. OPENAI_API_KEY is set in .env file")
            print("   2. API key is valid and has credits")
            print("   3. Network connection is working")
            state["error"] = "OpenAI GPT-4o-mini is not available. Please check your API key and network connection."
            return state
        
        # REUSE cached PDF knowledge (no new search needed!)
        user_choice_text = ""
        if user_answer is not None and user_answer < len(choices):
            user_choice_text = choices[user_answer].replace("A. ", "").replace("B. ", "").replace("C. ", "").replace("D. ", "")
        
        print(f"📚 Using cached PDF knowledge for explanation - choice: {user_choice_text}")
        cached_pdf = state.get("cached_pdf_knowledge", {})
        
        pdf_explanation_context = ""
        if cached_pdf.get("status") == "success" and cached_pdf.get("pdf_chunks"):
            # STRICT filtering for choice-specific content
            relevant_chunks = []
            if user_choice_text:
                choice_keywords = user_choice_text.lower().split()
                for chunk in cached_pdf["pdf_chunks"]:
                    content = chunk["content"].lower()
                    # Strict relevance: multiple choice keywords must match
                    keyword_matches = sum(1 for keyword in choice_keywords if keyword in content)
                    if keyword_matches >= max(1, len(choice_keywords) // 2):
                        relevant_chunks.append(chunk)
            else:
                # Fallback to general topic chunks if no specific choice
                relevant_chunks = cached_pdf["pdf_chunks"][:3]
            
            pdf_texts = [chunk["content"] for chunk in relevant_chunks[:2]]
            pdf_explanation_context = "\n\n".join(pdf_texts)
            if relevant_chunks:
                print(f"✅ Using cached PDF context: {len(pdf_explanation_context)} chars (filtered from cache)")
            else:
                print(f"⚠️ No relevant PDF context found for choice: {user_choice_text}")
        
        # Generate comprehensive explanation for ALL choices
        llm = ChatOpenAI(
            model=LLM_MODEL, 
            temperature=0.2,  # Lower temperature for more consistent explanations
            max_tokens=2048,
            top_p=0.95,
            seed=None  # Remove seed for variety
        )
        
        print(f"🤖 Using LLM: {LLM_MODEL} for answer evaluation")
        # Remove the connection test to avoid extra API calls
        print(f"✅ DIAGNOSTIC: Using LLM instance for answer evaluation")
        
        # Build choice explanations from cached data or generate new ones
        choice_explanations = state.get("choice_explanations", {})
        
        # Convert indices to letters for display
        choice_letters = ['A', 'B', 'C', 'D']
        
        # Clean choices to avoid duplication in explanations
        user_choice = choices[user_answer] if user_answer is not None and user_answer < len(choices) else "None"
        if user_choice != "None":
            user_choice = user_choice.replace('A. ', '').replace('B. ', '').replace('C. ', '').replace('D. ', '')
            
        correct_choice = choices[correct_answer] if correct_answer < len(choices) else "Unknown"
        if correct_choice != "Unknown":
            correct_choice = correct_choice.replace('A. ', '').replace('B. ', '').replace('C. ', '').replace('D. ', '')
        
        # Include PDF context in explanation
        context_section = ""
        if pdf_explanation_context:
            context_section = f"\n\nPDF KNOWLEDGE FOR EXPLANATION:\n{pdf_explanation_context[:1000]}"
        
        # Clean choices by removing existing A./B./C./D. prefixes to avoid duplication
        clean_choices = []
        for choice in choices:
            if choice:
                # Remove A./B./C./D. prefix if present
                clean_choice = choice.replace('A. ', '').replace('B. ', '').replace('C. ', '').replace('D. ', '')
                clean_choices.append(clean_choice)
            else:
                clean_choices.append('N/A')
        
        explanation_prompt = f"""You are an Expert NPTE Professor providing detailed explanations.

Topic: {topic}
Question: {state['question']}

User answered: {choice_letters[user_answer] if user_answer is not None else 'None'}. {user_choice}
Correct answer: {choice_letters[correct_answer]}. {correct_choice}
Result: {'CORRECT' if is_correct else 'INCORRECT'}

{context_section}

Use the PDF knowledge context above to inform your explanations with evidence-based reasoning.

Provide explanations in this EXACT format:

**ANSWER ANALYSIS:**

**{choice_letters[correct_answer]}. {correct_choice}** ✅ CORRECT ANSWER

**Explanation for each choice:**

A. {clean_choices[0] if len(clean_choices) > 0 else 'N/A'}
{'✅ CORRECT: ' if correct_answer == 0 else '❌ INCORRECT: '}{choice_explanations.get('0', f'Explain why this choice is {"correct" if correct_answer == 0 else "incorrect"} for {topic}')}

B. {clean_choices[1] if len(clean_choices) > 1 else 'N/A'}  
{'✅ CORRECT: ' if correct_answer == 1 else '❌ INCORRECT: '}{choice_explanations.get('1', f'Explain why this choice is {"correct" if correct_answer == 1 else "incorrect"} for {topic}')}

C. {clean_choices[2] if len(clean_choices) > 2 else 'N/A'}
{'✅ CORRECT: ' if correct_answer == 2 else '❌ INCORRECT: '}{choice_explanations.get('2', f'Explain why this choice is {"correct" if correct_answer == 2 else "incorrect"} for {topic}')}

D. {clean_choices[3] if len(clean_choices) > 3 else 'N/A'}
{'✅ CORRECT: ' if correct_answer == 3 else '❌ INCORRECT: '}{choice_explanations.get('3', f'Explain why this choice is {"correct" if correct_answer == 3 else "incorrect"} for {topic}')}

**Key Learning Points for {topic}:**
- Provide 2-3 specific learning points about {topic}
- Focus on current Physical Therapy applications, treatment planning, assessment, clinical reasoning, and evidence-based best practices
- Include Physical Therapy-specific contraindications, precautions, and common clinical errors
"""


        response = await llm.ainvoke([
            SystemMessage(content="You are an NPTE professor providing comprehensive explanations."),
            HumanMessage(content=explanation_prompt)
        ])
        
        state["explanation"] = response.content
        
        # ENHANCED: Get learning materials for BOTH user's choice AND correct choice
        user_choice_text = ""
        correct_choice_text = ""
        
        if user_answer is not None and user_answer < len(choices):
            user_choice_text = choices[user_answer].replace("A. ", "").replace("B. ", "").replace("C. ", "").replace("D. ", "")
        
        if correct_answer is not None and correct_answer < len(choices):
            correct_choice_text = choices[correct_answer].replace("A. ", "").replace("B. ", "").replace("C. ", "").replace("D. ", "")
        
        study_links = []
        
        if is_correct:
            # User got it right - provide ADVANCED materials on the correct choice for deeper learning
            print(f"🎯 Getting advanced materials for correct choice: {correct_choice_text}")
            try:
                correct_links = await get_topic_focused_links.ainvoke({
                    "topic": topic, 
                    "is_correct": True,  # Advanced/evidence-based materials
                    "choice_content": correct_choice_text,
                    "question_text": question_text,
                    "all_choices": choices
                })
                print(f"🎯 Found {len(correct_links)} advanced links for correct choice: {correct_choice_text}")
                study_links.extend(correct_links[:3])  # More links for deeper study
                
                # FALLBACK: If no advanced links found, try general approach
                if len(correct_links) == 0:
                    print(f"⚠️ No advanced links found, trying general approach for: {correct_choice_text}")
                    fallback_links = await get_topic_focused_links.ainvoke({
                        "topic": topic,
                        "is_correct": False,  # Use general study approach
                        "choice_content": correct_choice_text,
                        "question_text": question_text,
                        "all_choices": choices
                    })
                    study_links.extend(fallback_links[:3])
                    print(f"📚 Added {len(fallback_links[:3])} fallback links for correct choice")
                    
            except Exception as e:
                print(f"⚠️ Failed to get correct choice links: {e}")
                # Try one more fallback without choice-specific content
                try:
                    general_links = await get_topic_focused_links.ainvoke({
                        "topic": topic,
                        "is_correct": True,
                        "choice_content": "",  # General topic search
                        "question_text": question_text,
                        "all_choices": choices
                    })
                    study_links.extend(general_links[:2])
                    print(f"📚 Added {len(general_links[:2])} general topic links")
                except Exception as e2:
                    print(f"⚠️ Even general links failed: {e2}")
                    
            print(f"📋 Total study links for correct answer: {len(study_links)}")
            
        else:
            # User got it wrong - provide materials for BOTH their wrong choice AND the correct choice
            print(f"📚 Getting study materials for incorrect choice: {user_choice_text}")
            print(f"🎯 Plus advanced materials for correct choice: {correct_choice_text}")
            
            # Materials about why their choice was wrong
            try:
                wrong_links = await get_topic_focused_links.ainvoke({
                    "topic": topic, 
                    "is_correct": False,  # Study guides/fundamentals
                    "choice_content": user_choice_text,
                    "question_text": question_text,
                    "all_choices": choices
                })
                print(f"📚 Found {len(wrong_links)} links for incorrect choice: {user_choice_text}")
                study_links.extend(wrong_links[:2])     # Why their choice was wrong
            except Exception as e:
                print(f"⚠️ Failed to get wrong choice links: {e}")
            
            # Materials about the correct choice (advanced) - ALWAYS try to get these
            try:
                correct_links = await get_topic_focused_links.ainvoke({
                    "topic": topic, 
                    "is_correct": True,  # Advanced/evidence-based materials
                    "choice_content": correct_choice_text,
                    "question_text": question_text,
                    "all_choices": choices
                })
                print(f"🎯 Found {len(correct_links)} links for correct choice: {correct_choice_text}")
                study_links.extend(correct_links[:2])   # What the correct choice is about
            except Exception as e:
                print(f"⚠️ Failed to get correct choice links: {e}")
            
            # FALLBACK: Ensure we have at least some learning materials
            if len(study_links) == 0:
                print(f"⚠️ No specific choice links found, getting general topic materials...")
                try:
                    fallback_links = await get_topic_focused_links.ainvoke({
                        "topic": topic,
                        "is_correct": False,
                        "choice_content": "",  # General topic search
                        "question_text": question_text,
                        "all_choices": choices
                    })
                    study_links.extend(fallback_links[:2])
                    print(f"📚 Added {len(fallback_links[:2])} fallback links")
                except Exception as e:
                    print(f"⚠️ Even fallback links failed: {e}")
            
            print(f"📋 Total study links collected: {len(study_links)}")
        
        state["study_links"] = study_links
        
        # FIXED: Always show both continue and topic selection options
        state["continue_available"] = not is_correct  # Show continue button for wrong answers
        state["topic_selection_available"] = True  # Always allow topic selection
        
        print(f"✅ Generated comprehensive explanation with {len(study_links)} focused links")
        return state
        
    except Exception as e:
        state["error"] = f"Answer evaluation failed: {e}"
        return state

async def format_final_response_node(state: NPTEState, config: RunnableConfig) -> NPTEState:
    """
    FIXED: Format final response with proper button availability
    """
    try:
        # Ensure continue logic is correct
        is_correct = state.get("is_correct", False)
        
        # FIXED: Button availability logic
        state["continue_available"] = not is_correct  # Continue only for incorrect answers
        state["topic_selection_available"] = True    # Always allow new topic selection
        
        print(f"📋 Final response formatted:")
        print(f"   Continue available: {state['continue_available']}")
        print(f"   Topic selection available: {state['topic_selection_available']}")
        
        return state
        
    except Exception as e:
        state["error"] = f"Response formatting failed: {e}"
        return state

# ============================================================================
# ROUTING LOGIC - SIMPLIFIED
# ============================================================================

def should_continue_topic(state: NPTEState) -> str:
    """Simple routing: continue same topic or end"""
    if state.get("continue_topic", False):
        return "generate_question"
    return END

def needs_evaluation(state: NPTEState) -> str:
    """Check if user provided an answer"""
    if state.get("user_answer_index") is not None:
        return "evaluate_answer"
    return "wait_for_answer"  # In real app, this would pause execution

# ============================================================================
# GRAPH CONSTRUCTION - CLEAN FLOW
# ============================================================================

def create_npte_graph() -> StateGraph:
    """
    FIXED: Clean, linear graph flow
    Topic → Generate Question → User Answers → Evaluate → Format Response → END
    """
    workflow = StateGraph(NPTEState)
    
    # Add nodes
    workflow.add_node("generate_question", generate_question_node)
    workflow.add_node("evaluate_answer", evaluate_answer_node) 
    workflow.add_node("format_response", format_final_response_node)
    
    # Linear flow
    workflow.add_edge(START, "generate_question")
    workflow.add_edge("generate_question", "evaluate_answer")
    workflow.add_edge("evaluate_answer", "format_response")
    workflow.add_edge("format_response", END)
    
    # Compile with memory
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app

# ============================================================================
# FASTAPI INTEGRATION - SIMPLIFIED
# ============================================================================

class NPTEProfessorAgent:
    """
    FIXED: Simplified Professor Agent for FastAPI integration
    Addresses all 4 identified issues
    """
    
    def __init__(self):
        self.graph_app = create_npte_graph()
        self.session_cache = {}  # Simple session cache
        print("🎓 NPTE Professor Agent initialized (FIXED version)")
    
    def _format_pdf_source(self, raw_source: str, metadata: dict) -> str:
        """
        Format PDF source for student lookup with journal/publication info
        """
        try:
            # Extract potential journal/publication info from metadata
            title = metadata.get('title', '')
            journal = metadata.get('journal', '')
            source = metadata.get('source', raw_source)
            
            # Common journal abbreviations mapping
            journal_mappings = {
                'jspt': 'IJSPT',
                'ijspt': 'IJSPT', 
                'jospt': 'JOSPT',
                'jopt': 'JOPT',
                'apta': 'APTA',
                'physical therapy': 'Physical Therapy Journal',
                'physiotherapy': 'Physiotherapy',
                'jama': 'JAMA',
                'pubmed': 'PubMed',
                'ncbi': 'NCBI',
                'ajpmr': 'AJPM&R',
                'aipmr': 'AIPMR'
            }
            
            # Try to identify journal from filename or metadata
            source_lower = source.lower()
            identified_journal = None
            
            for key, journal_name in journal_mappings.items():
                if key in source_lower or key in journal.lower():
                    identified_journal = journal_name
                    break
            
            # Format based on available information
            if identified_journal and title:
                # Best case: Journal + Title
                clean_title = title.replace('.pdf', '').replace('_', ' ').strip()
                return f"{identified_journal}: {clean_title}"
            elif identified_journal:
                # Journal + filename
                clean_filename = raw_source.replace('.pdf', '').replace('_', ' ').strip()
                return f"{identified_journal}: {clean_filename}"
            elif title:
                # Just title (research paper)
                clean_title = title.replace('.pdf', '').replace('_', ' ').strip()
                return f"Research: {clean_title}"
            else:
                # Fallback: clean filename only if it looks academic
                clean_filename = raw_source.replace('.pdf', '').replace('_', ' ').strip()
                if any(term in clean_filename.lower() for term in ['study', 'research', 'clinical', 'therapy', 'treatment']):
                    return f"Study: {clean_filename}"
                else:
                    # Skip non-academic looking sources
                    return None
                    
        except Exception as e:
            print(f"⚠️ PDF source formatting failed: {e}")
            return None
    
    async def generate_mcq(self, topic: str, session_id: str = "default") -> Dict:
        """
        ISSUE #1 FIXED: Generate MCQ with topic-focused links
        ISSUE #3 FIXED: Proper explanation format for all choices
        """
        try:
            print(f"📚 Generating MCQ for topic: {topic}")
            
            config = RunnableConfig(
                configurable={"thread_id": session_id}
            )
            
            initial_state = {
                "topic": topic,
                "question": None,
                "choices": None,
                "correct_answer_index": None,
                "user_answer_index": None,
                "is_correct": None,
                "explanation": None,
                "study_links": None,
                "continue_topic": False,
                "choice_explanations": None,
                "continue_available": False,
                "topic_selection_available": True,
                "error": None
            }
            
            # Execute graph - only generate question
            result = await self.graph_app.ainvoke(initial_state, config)
            
            # Cache for evaluation (including PDF knowledge for reuse)
            cached_data = {
                "topic": result.get("topic"),
                "question": result.get("question"),  
                "choices": result.get("choices"),
                "correct_answer_index": result.get("correct_answer_index"),
                "choice_explanations": result.get("choice_explanations", {}),
                "cached_pdf_knowledge": result.get("cached_pdf_knowledge", {})
            }
            
            self.session_cache[session_id] = cached_data
            print(f"✅ Cached session {session_id} with topic: {cached_data.get('topic')}")
            print(f"🔍 Cache now contains {len(self.session_cache)} sessions")
            
            # Generate choice-specific learning links
            topic = result.get("topic", "")
            choices = result.get("choices", [])
            correct_idx = result.get("correct_answer_index", 0)
            links = {}
            
            try:
                # REUSE cached PDF knowledge for choice-specific sources (efficient!)
                cached_pdf = result.get("cached_pdf_knowledge", {})
                
                # Generate web links and filter cached PDFs for each choice
                for i, choice in enumerate(choices):
                    is_correct_choice = (i == correct_idx)
                    
                    # Create choice-specific search query
                    choice_text = choice.replace("A. ", "").replace("B. ", "").replace("C. ", "").replace("D. ", "")
                    
                    print(f"🔗 Generating sources for choice {i}: {'✅ CORRECT' if is_correct_choice else '❌ INCORRECT'}")
                    
                    # FIXED: Strict relevance filtering and proper source formatting
                    choice_pdf_sources = []
                    if cached_pdf.get("status") == "success" and cached_pdf.get("pdf_chunks"):
                        choice_keywords = choice_text.lower().split()
                        
                        for chunk in cached_pdf["pdf_chunks"]:
                            content = chunk["content"].lower()
                            
                            # STRICT relevance check: multiple keywords must match
                            keyword_matches = sum(1 for keyword in choice_keywords if keyword in content)
                            relevance_threshold = max(1, len(choice_keywords) // 2)  # At least half the keywords
                            
                            if keyword_matches >= relevance_threshold:
                                # Format PDF source properly for student lookup
                                metadata = chunk.get("metadata", {})
                                raw_source = chunk.get("pdf_source", "Unknown PDF")
                                
                                # Extract journal/publication info from metadata or filename
                                formatted_source = self._format_pdf_source(raw_source, metadata)
                                
                                # Only include if formatting was successful (relevant academic source)
                                if formatted_source and formatted_source not in choice_pdf_sources:
                                    choice_pdf_sources.append(formatted_source)
                                    print(f"📄 Choice {i} relevant in: {formatted_source}")
                                    break  # One relevant PDF source per choice
                        
                        if not choice_pdf_sources:
                            print(f"📄 Choice {i}: No sufficiently relevant PDF sources found")
                    
                    # Get choice-specific web links
                    choice_links = await get_topic_focused_links.ainvoke({
                        "topic": topic,
                        "is_correct": is_correct_choice,
                        "choice_content": choice_text,
                        "question_text": result.get("question", ""),
                        "all_choices": choices
                    })
                    
                    # Combine web links and cached PDF sources
                    all_sources = choice_links[:1] + choice_pdf_sources[:1]  # 1 web link + 1 PDF source
                    links[str(i)] = all_sources[:2]  # Max 2 sources per choice
                    
            except Exception as e:
                print(f"⚠️ Choice-specific link generation failed: {e}")
                # Fallback: Generate general topic links
                try:
                    fallback_links = await get_topic_focused_links.ainvoke({
                        "topic": topic,
                        "is_correct": False,
                        "choice_content": "",  # Fallback to general topic search
                        "question_text": result.get("question", ""),
                        "all_choices": choices
                    })
                    links = {str(i): fallback_links[:1] for i in range(len(choices))}
                except:
                    links = {str(i): [] for i in range(len(choices))}
            
            # Return in expected format
            return {
                "question": result.get("question", ""),
                "choices": result.get("choices", []),
                "correct": result.get("correct_answer_index", 0),
                "explanations": result.get("choice_explanations", {}),
                "links": links
            }
            
        except Exception as e:
            print(f"❌ MCQ generation failed: {e}")
            return {
                "question": f"Error generating question for {topic}: {e}",
                "choices": ["A. Error", "B. Error", "C. Error", "D. Error"],
                "correct": 0,
                "explanations": {str(i): f"Error: {e}" for i in range(4)},
                "links": {str(i): [] for i in range(4)}
            }
    
    async def evaluate_answer(self, session_id: str, user_answer_index: int) -> Dict:
        """
        ISSUE #3 FIXED: Return comprehensive explanations for ALL choices
        ISSUE #4 FIXED: Proper button availability (continue + topic selection)
        """
        try:
            print(f"🔍 Looking for session {session_id} in cache...")
            print(f"🔍 Available sessions: {list(self.session_cache.keys())}")
            
            cached_data = self.session_cache.get(session_id)
            if not cached_data:
                print(f"❌ Session {session_id} not found in cache!")
                return {
                    "is_correct": False,
                    "explanation": "Error: No question data found. Please generate a new question.",
                    "study_links": [],
                    "continue_available": False,
                    "topic_selection_available": True
                }
            
            print(f"📊 Evaluating answer for session {session_id}")
            
            config = RunnableConfig(
                configurable={"thread_id": session_id}
            )
            
            # Create evaluation state with cached data (including PDF knowledge)
            eval_state = {
                "topic": cached_data["topic"],
                "question": cached_data["question"],
                "choices": cached_data["choices"], 
                "correct_answer_index": cached_data["correct_answer_index"],
                "choice_explanations": cached_data["choice_explanations"],
                "cached_pdf_knowledge": cached_data.get("cached_pdf_knowledge", {}),
                "user_answer_index": user_answer_index,
                "is_correct": None,
                "explanation": None,
                "study_links": None,
                "continue_topic": False,
                "continue_available": None,
                "topic_selection_available": None,
                "error": None
            }
            
            print(f"🔍 DEBUG: eval_state user_answer_index = {eval_state['user_answer_index']}")
            
            # Execute evaluation and formatting nodes
            result = await self.graph_app.ainvoke(eval_state, config)
            
            is_correct = result.get("is_correct", False)
            
            # Enhanced study links with clear labeling
            study_links = result.get("study_links", [])
            study_message = ""
            
            if is_correct:
                correct_choice = cached_data['choices'][cached_data['correct_answer_index']].replace('A. ', '').replace('B. ', '').replace('C. ', '').replace('D. ', '')
                study_message = f"🎯 Advanced resources for deeper understanding of: {correct_choice}"
            else:
                user_choice = cached_data['choices'][user_answer_index].replace('A. ', '').replace('B. ', '').replace('C. ', '').replace('D. ', '')
                correct_choice = cached_data['choices'][cached_data['correct_answer_index']].replace('A. ', '').replace('B. ', '').replace('C. ', '').replace('D. ', '')
                study_message = f"📚 Learning materials: Why '{user_choice}' may not be ideal + mastering '{correct_choice}' (correct approach)"
            
            return {
                "is_correct": is_correct,
                "explanation": result.get("explanation", "No explanation available"),
                "study_links": study_links,
                "study_message": study_message,
                "continue_available": not is_correct,  # FIXED: Continue only for wrong answers
                "topic_selection_available": True,     # FIXED: Always allow topic selection
                "continue_message": f"Would you like to continue practicing {cached_data['topic']}?" if not is_correct else ""
            }
            
        except Exception as e:
            print(f"❌ Answer evaluation failed: {e}")
            return {
                "is_correct": False,
                "explanation": f"Evaluation failed: {e}",
                "study_links": [],
                "continue_available": False,
                "topic_selection_available": True
            }
    
    async def continue_same_topic(self, session_id: str) -> Dict:
        """
        FIXED: Continue with same topic - generate new question
        """
        try:
            cached_data = self.session_cache.get(session_id)
            if not cached_data:
                return {"error": "No session data found"}
            
            topic = cached_data["topic"]
            print(f"🔄 Continuing with topic: {topic}")
            
            # Generate new question for same topic
            return await self.generate_mcq(topic, session_id)
            
        except Exception as e:
            return {"error": f"Continue failed: {e}"}

# ============================================================================
# INTEGRATION NOTES FOR FRONTEND
# ============================================================================

"""
FRONTEND FIXES NEEDED (Issue #2):

In your React component, add loading state management:

const [isGenerating, setIsGenerating] = useState(false);
const [isEvaluating, setIsEvaluating] = useState(false);

// When generating question
const handleTopicSelect = async (topic) => {
  setIsGenerating(true);
  // Disable all choice buttons
  setChoicesDisabled(true);
  
  try {
    const response = await fetch('/api/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: topic })
    });
    const mcq = await response.json();
    setCurrentMCQ(mcq);
    // Re-enable choice buttons
    setChoicesDisabled(false);
  } finally {
    setIsGenerating(false);
  }
};

// When evaluating answer  
const handleAnswerSelect = async (answerIndex) => {
  setIsEvaluating(true);
  // Disable all buttons during evaluation
  setChoicesDisabled(true);
  setContinueDisabled(true);
  setTopicSelectDisabled(true);
  
  try {
    const response = await fetch('/api/evaluate', {
      method: 'POST', 
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        session_id: sessionId,
        user_answer_index: answerIndex 
      })
    });
    const result = await response.json();
    
    // Show results and enable appropriate buttons
    setEvaluationResult(result);
    setContinueDisabled(!result.continue_available);
    setTopicSelectDisabled(!result.topic_selection_available);
    
  } finally {
    setIsEvaluating(false);
  }
};

// In your JSX:
<button 
  onClick={() => handleAnswerSelect(index)}
  disabled={isGenerating || isEvaluating || choicesDisabled}
>
  {choice}
</button>

<button 
  onClick={handleContinueSameTopic}
  disabled={!evaluationResult?.continue_available || isGenerating || isEvaluating}
>
  Continue {topic}
</button>

<button 
  onClick={handleSelectNewTopic}  
  disabled={!evaluationResult?.topic_selection_available || isGenerating || isEvaluating}
>
  Choose New Topic
</button>
"""

# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    async def test_agent():
        agent = NPTEProfessorAgent()
        
        # Test MCQ generation
        print("🧪 Testing MCQ generation...")
        mcq = await agent.generate_mcq("musculoskeletal system", "test")
        print(f"Generated: {mcq['question'][:100]}...")
        
        # Test evaluation
        print("\n🧪 Testing answer evaluation...")
        eval_result = await agent.evaluate_answer("test", 1)  # Wrong answer
        print(f"Evaluation: {eval_result['is_correct']}")
        print(f"Continue available: {eval_result['continue_available']}")
        print(f"Topic selection available: {eval_result['topic_selection_available']}")
    
    asyncio.run(test_agent())
