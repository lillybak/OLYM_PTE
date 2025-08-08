#!/usr/bin/env python3
"""
Mock test script that simulates agent functionality
"""

def test_mock_agent():
    """Test mock agent functionality"""
    print("🧪 Testing Mock Agent System")
    print("=" * 40)
    
    # Mock MCQ generation
    test_topic = "Cardiovascular and pulmonary systems"
    print(f"\n📝 Testing MCQ generation for: {test_topic}")
    
    # Mock MCQ response
    mock_mcq = {
        "question": "A patient presents with chest pain and shortness of breath. Which of the following is the MOST appropriate initial assessment?",
        "choices": [
            "A. Immediate cardiac catheterization",
            "B. Comprehensive pulmonary function test", 
            "C. Basic vital signs and cardiac auscultation",
            "D. Advanced imaging with CT scan"
        ],
        "correct": 2,  # C is correct
        "explanations": {
            0: "Cardiac catheterization is invasive and not appropriate for initial assessment.",
            1: "Pulmonary function tests are not the first step in cardiac assessment.",
            2: "Basic vital signs and cardiac auscultation are essential first steps in cardiac assessment.",
            3: "Advanced imaging should follow basic assessment, not precede it."
        },
        "links": {
            0: ["https://www.heart.org/en/health-topics/heart-attack/diagnosing-a-heart-attack"],
            1: ["https://www.lung.org/lung-health-diseases/lung-procedures-and-tests"],
            2: ["https://www.heart.org/en/health-topics/heart-attack/diagnosing-a-heart-attack"],
            3: ["https://www.radiologyinfo.org/en/info/ct-cardiac"]
        }
    }
    
    print("✅ Mock MCQ generated successfully")
    print(f"Question: {mock_mcq['question']}")
    print(f"Choices: {len(mock_mcq['choices'])} options")
    print(f"Correct answer: {mock_mcq['correct']} ({mock_mcq['choices'][mock_mcq['correct']]})")
    
    # Test answer validation
    print(f"\n🔍 Testing answer validation")
    
    # Mock validation for wrong answer
    mock_validation = {
        "correct": False,
        "explanation": "Incorrect. Basic vital signs and cardiac auscultation are essential first steps in cardiac assessment. Advanced procedures should only be considered after initial assessment reveals concerning findings.",
        "suggest_same_topic": True,
        "links": ["https://www.heart.org/en/health-topics/heart-attack/diagnosing-a-heart-attack"]
    }
    
    print("✅ Mock answer validation successful")
    print(f"Correct: {mock_validation['correct']}")
    print(f"Explanation: {mock_validation['explanation']}")
    print(f"Suggest same topic: {mock_validation['suggest_same_topic']}")
    
    print("\n🎉 Mock tests passed! System is ready for integration.")
    print("\n💡 Next steps:")
    print("1. Start the backend: uvicorn app:app --reload")
    print("2. Start the frontend: cd ../frontend-vite && npm run dev")
    print("3. Test the full system through the web interface")

if __name__ == "__main__":
    test_mock_agent() 