#!/usr/bin/env python3
"""
Ollama-based NPTE Agent System
"""

import os
import json
import requests
from typing import Dict, List, Optional
import time

class OllamaAgent:
    """NPTE Agent using Ollama for LLM calls"""
    
    def __init__(self, model_name: str = "qwen:latest"):
        self.model_name = model_name
        self.base_url = "http://localhost:11434"

        
    def _call_ollama(self, prompt: str, system_prompt: str = "") -> str:
        """Call Ollama API"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "format": "json"
            }
            print(f"[{time.strftime('%H:%M:%S')}] Payload: {payload}")
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=240)
            print(f"[{time.strftime('%H:%M:%S')}] running ollama_agent.py")
            print(f"[{time.strftime('%H:%M:%S')}] Response: {response}")
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] Ollama API error: {e}")
            return ""
    
    def generate_mcq(self, topic: str) -> Dict:
        """Generate NPTE-style MCQ for given topic"""
        
        system_prompt = """You are an NPTE-PT exam tutor. Generate a multiple-choice question with specific content.

IMPORTANT: Return ONLY a valid JSON object with real content. Do not use generic placeholders. Use scenario-style queations as in the Example format. Don not use content from the "Example format"

Example format:
{
  "question": "A 20-year-old male football player presents to the clinic with an ankle injury. The patient was tackled while his foot was stuck in the grass. He can take 5-6 steps at a time due to pain and has only mild ankle swelling. There is no tenderness over the lateral or medial malleoli. He had a negative talar tilt test and anterior drawer but a positive Kleiger’s test. Which of the following diagnoses is MOST consistent with the patient’s symptoms?",
  "choices": [
    "A. Ankle fracture" 
    "B. Grade II lateral ankle sprain",
    "C. Grade III lateral ankle sprain",
    "D. High-ankle sprain"
  ],
  
  The correct answer is 4: High-ankle sprain: 
  "Explanation: 
  The mechanism is consistent with a syndesmotic AKA high ankle sprain, which involves forced dorsiflexion and external rotation on a fixed foot. The Kleiger test is a test for a high ankle sprain."
  The other choices are incorrect because:
1.  Ankle fracture-While an inability to bear weight is a piece of the Ottawa ankle rules, the criteria is inability to take 4 steps, not 5-6 steps. They do not have bony tenderness over the malleoli, making a fracture less likely.
2.  Grade II lateral ankle sprain: This would present with moderate pain and swelling, but weightbearing should still be possible. An anterior drawer and talar tilt test would be positive.
3.  Grade III lateral ankle sprain: This often presents with severe pain, bruising, and swelling. The patient may not be able to bear weight. An anterior drawer and talar tilt test would be positive and more severe than a grade II sprain.
  },
  "links": {
    "0": ["https://apta.org/clinical-practice-guidelines"],
    "1": ["https://apta.org/assessment-guidelines"],
    "2": ["https://apta.org/cardiac-assessment"],
    "3": ["https://apta.org/respiratory-therapy"]
  }
}

Rules:
-  The choices must be labeled A, B, C, D
- Each choice must be a unique answer
- One and only one of the choices must be the correct answer
- Do NOT use generic placeholders like "Option A" or "Explanation for option X".
- 'correct' is 0-based (0=A, 1=B, 2=C, 3=D)
- For each choice provide a detailed explanation for why it is correct or incorrect
- Provide relevant learning links for each choice
- Make content specific to the topic, not generic"""

        prompt = f"""Generate a multiple-choice question about: {topic}

CRITICAL: You must provide:
1. A specific one-paragraph scenario followed by the question on {topic}
2. The wrong answers should be somewhat similar to the correct answer.

Make everything specific to {topic}."""

        response = self._call_ollama(prompt, system_prompt)
        
        print(f"[{time.strftime('%H:%M:%S')}] Raw Ollama response: {response[:500]}...")
        
        # Try to extract JSON from response
        try:
            # Find JSON in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                print(f"[{time.strftime('%H:%M:%S')}] Extracted JSON: {json_str}")
                mcq_data = json.loads(json_str)
                
                # Ensure all required fields are present with fallbacks
                if 'question' not in mcq_data or not mcq_data['question']:
                    mcq_data['question'] = f"Sample question about {topic}"
                
                if 'choices' not in mcq_data or not mcq_data['choices']:
                    mcq_data['choices'] = ["A. Option A", "B. Option B", "C. Option C", "D. Option D"]
                
                if 'correct' not in mcq_data:
                    mcq_data['correct'] = 0
                
                # Ensure explanations dict exists and has entries for all choices
                if 'explanations' not in mcq_data or mcq_data['explanations'] is None:
                    mcq_data['explanations'] = {}
                
                # Handle both numeric and letter keys in explanations
                for i in range(len(mcq_data['choices'])):
                    # Check for numeric key first
                    if str(i) not in mcq_data['explanations']:
                        # Check for letter key (A=0, B=1, C=2, D=3)
                        letter_key = chr(65 + i)  # A, B, C, D
                        if letter_key in mcq_data['explanations']:
                            mcq_data['explanations'][str(i)] = mcq_data['explanations'][letter_key]
                        else:
                            mcq_data['explanations'][str(i)] = f"Explanation for option {i}"
                
                # Ensure links dict exists and has entries for all choices
                if 'links' not in mcq_data or mcq_data['links'] is None:
                    mcq_data['links'] = {}
                
                for i in range(len(mcq_data['choices'])):
                    if str(i) not in mcq_data['links']:
                        mcq_data['links'][str(i)] = ["https://apta.org"]
                
                # Clean up any letter keys that might be left in explanations
                keys_to_remove = []
                for key in mcq_data['explanations']:
                    if key in ['A', 'B', 'C', 'D']:
                        keys_to_remove.append(key)
                
                for key in keys_to_remove:
                    del mcq_data['explanations'][key]
                
                # Check if we got generic content and try to improve it
                if any("Option A" in choice for choice in mcq_data['choices']):
                    print(f"Warning: Received generic choices for topic '{topic}'. This may indicate the model didn't follow the prompt properly.")
                
                if any("Explanation for option" in exp for exp in mcq_data['explanations'].values()):
                    print(f"Warning: Received generic explanations for topic '{topic}'. This may indicate the model didn't follow the prompt properly.")
                
                return mcq_data
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            print(f"Failed to parse Ollama response: {e}")
            # Return a fallback MCQ to prevent crashes
            return {
                "question": f"What is the primary function of the {topic.lower()}?",
                "choices": [
                    f"A. Primary function of {topic.lower()}",
                    f"B. Secondary function of {topic.lower()}",
                    f"C. Tertiary function of {topic.lower()}",
                    f"D. None of the above"
                ],
                "correct": 0,
                "explanations": {
                    "0": f"Correct. The primary function of {topic.lower()} is essential for proper body function.",
                    "1": f"Incorrect. This is a secondary function of {topic.lower()}.",
                    "2": f"Incorrect. This is a tertiary function of {topic.lower()}.",
                    "3": f"Incorrect. There are specific functions of {topic.lower()}."
                },
                "links": {
                    "0": ["https://apta.org/clinical-practice-guidelines"],
                    "1": ["https://apta.org/assessment-guidelines"],
                    "2": ["https://apta.org/treatment-guidelines"],
                    "3": ["https://apta.org/education-resources"]
                }
            }
    
    # Removed validate_answer method - validation now handled client-side
    


def get_ollama_agent() -> OllamaAgent:
    """Get Ollama agent instance"""
    return OllamaAgent() 