#!/usr/bin/env python3
"""
Test script for the NPTE Agent System
"""

from agent_system import get_agent

def test_agent():
    """Test the agent system"""
    print("🧪 Testing NPTE Agent System")
    print("=" * 40)
    
    # Initialize agent
    try:
        agent = get_agent()
        print("✅ Agent initialized successfully")
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return
    
    # Test MCQ generation
    test_topic = "Cardiovascular and pulmonary systems"
    print(f"\n📝 Testing MCQ generation for: {test_topic}")
    
    try:
        mcq = agent.generate_mcq(test_topic)
        print("✅ MCQ generated successfully")
        print(f"Question: {mcq['question'][:100]}...")
        print(f"Choices: {len(mcq['choices'])} options")
        print(f"Correct answer: {mcq['correct']}")
    except Exception as e:
        print(f"❌ MCQ generation failed: {e}")
        return
    
    # Test answer validation
    print(f"\n🔍 Testing answer validation")
    try:
        validation = agent.validate_answer(
            test_topic,
            selected_answer=1,  # Wrong answer
            correct_answer=mcq['correct'],
            explanations=mcq['explanations']
        )
        print("✅ Answer validation successful")
        print(f"Correct: {validation['correct']}")
        print(f"Explanation: {validation['explanation'][:100]}...")
        print(f"Suggest same topic: {validation['suggest_same_topic']}")
    except Exception as e:
        print(f"❌ Answer validation failed: {e}")
        return
    
    print("\n🎉 All tests passed! Agent system is working correctly.")

if __name__ == "__main__":
    test_agent() 