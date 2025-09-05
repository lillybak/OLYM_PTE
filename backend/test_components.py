"""
Comprehensive test script for NPTE LangGraph components
Tests all 4 fixed issues systematically
"""

import asyncio
import sys
import os

# Add backend path for RAG system import
sys.path.append('/home/olb/demo2025/demo-OLYM_PTE/backend')

# Note: Make sure to copy your embeddings first:
# cp -r ~/NPTE_Oly/OLYM_PTE/backend/qdrant_data_txt-3 /home/olb/demo2025/demo-OLYM_PTE/backend/

from npte_langgraph_fixed import NPTEProfessorAgent, query_pdf_knowledge, get_topic_focused_links

async def test_pdf_rag_integration():
    """Test Issue Fix: PDF RAG integration"""
    print("\n🧪 TEST 1: PDF RAG Integration")
    print("=" * 50)
    
    try:
        # Test PDF knowledge query
        result = await query_pdf_knowledge.ainvoke({
            "topic": "musculoskeletal system",
            "query": "shoulder assessment"
        })
        
        if result.get("status") == "success":
            chunks = result.get("pdf_chunks", [])
            print(f"✅ PDF RAG working: Found {len(chunks)} relevant chunks")
            if chunks:
                print(f"📄 Sample content: {chunks[0]['content'][:100]}...")
        else:
            print(f"❌ PDF RAG failed: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ PDF RAG test failed: {e}")

async def test_topic_focused_links():
    """Test Issue Fix #1: Topic-focused links"""
    print("\n🧪 TEST 2: Topic-Focused Links")
    print("=" * 50)
    
    try:
        # Test for correct answer (advanced materials)
        correct_links = await get_topic_focused_links("musculoskeletal system", is_correct=True)
        print(f"✅ Correct answer links: {len(correct_links)} links")
        for i, link in enumerate(correct_links[:2], 1):
            print(f"   {i}. {link}")
        
        # Test for incorrect answer (study materials)
        incorrect_links = await get_topic_focused_links("musculoskeletal system", is_correct=False)
        print(f"✅ Incorrect answer links: {len(incorrect_links)} links")
        for i, link in enumerate(incorrect_links[:2], 1):
            print(f"   {i}. {link}")
            
    except Exception as e:
        print(f"❌ Topic-focused links test failed: {e}")

async def test_mcq_generation():
    """Test MCQ generation with PDF context"""
    print("\n🧪 TEST 3: MCQ Generation with PDF Context")
    print("=" * 50)
    
    try:
        agent = NPTEProfessorAgent()
        
        # Test question generation
        mcq = await agent.generate_mcq("cardiovascular and pulmonary system", "test_session")
        
        print(f"✅ Question generated:")
        print(f"📝 Topic focus: {'cardiovascular' in mcq['question'].lower() or 'pulmonary' in mcq['question'].lower()}")
        print(f"🎯 Question: {mcq['question'][:150]}...")
        print(f"🔤 Choices format: {mcq['choices'][0][:10]}")  # Should start with "A."
        print(f"📊 Correct answer: {mcq['correct']}")
        
    except Exception as e:
        print(f"❌ MCQ generation test failed: {e}")

async def test_comprehensive_evaluation():
    """Test Issue Fix #3: Comprehensive explanations for ALL choices"""
    print("\n🧪 TEST 4: Comprehensive Answer Evaluation")
    print("=" * 50)
    
    try:
        agent = NPTEProfessorAgent()
        
        # Generate question first
        mcq = await agent.generate_mcq("neuromuscular and nervous systems", "eval_test")
        print(f"📝 Generated question for evaluation test")
        
        # Test wrong answer evaluation
        eval_result = await agent.evaluate_answer("eval_test", 1)  # Assume wrong answer
        
        print(f"✅ Evaluation completed:")
        print(f"📊 Is correct: {eval_result['is_correct']}")
        print(f"📝 Explanation length: {len(eval_result['explanation'])} chars")
        print(f"🔗 Study links: {len(eval_result['study_links'])} links")
        
        # Check if explanation covers all choices
        explanation = eval_result['explanation']
        has_all_choices = all(f"{letter}." in explanation for letter in ['A', 'B', 'C', 'D'])
        print(f"✅ All choices explained: {has_all_choices}")
        
        # Issue Fix #4: Button availability logic
        print(f"🔘 Continue available: {eval_result['continue_available']}")
        print(f"🔘 Topic selection available: {eval_result['topic_selection_available']}")
        
    except Exception as e:
        print(f"❌ Comprehensive evaluation test failed: {e}")

async def test_continue_functionality():
    """Test Issue Fix #4: Continue same topic functionality"""
    print("\n🧪 TEST 5: Continue Same Topic")
    print("=" * 50)
    
    try:
        agent = NPTEProfessorAgent()
        
        # Generate first question
        mcq1 = await agent.generate_mcq("integumentary system", "continue_test")
        print(f"✅ First question: {mcq1['question'][:100]}...")
        
        # Simulate wrong answer to trigger continue option
        eval_result = await agent.evaluate_answer("continue_test", 0)  # Assume wrong
        
        if eval_result['continue_available']:
            # Test continue functionality
            mcq2 = await agent.continue_same_topic("continue_test")
            print(f"✅ Continued question: {mcq2['question'][:100]}...")
            print(f"🔄 Different question: {mcq1['question'] != mcq2['question']}")
        else:
            print("❌ Continue not available (unexpected)")
            
    except Exception as e:
        print(f"❌ Continue functionality test failed: {e}")

async def main():
    """Run all tests"""
    print("🚀 NPTE LangGraph System - Comprehensive Test Suite")
    print("Testing all 4 issue fixes + PDF RAG integration")
    
    # Test individual components
    await test_pdf_rag_integration()
    await test_topic_focused_links()
    await test_mcq_generation()
    await test_comprehensive_evaluation()
    await test_continue_functionality()
    
    print("\n" + "=" * 50)
    print("🎉 Test suite completed!")
    print("Check above for ✅ (pass) or ❌ (fail) indicators")

if __name__ == "__main__":
    asyncio.run(main())
