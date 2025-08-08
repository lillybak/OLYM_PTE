import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from random import randint
import openai
from dotenv import load_dotenv
import json
import re

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

class PromptRequest(BaseModel):
    prompt: str

class MCQResponse(BaseModel):
    question: str
    choices: list[str]
    correct: int
    explanations: dict
    links: dict

@app.post("/api/ask", response_model=MCQResponse)
async def ask(request: PromptRequest):
    # HERE: LLM call is commented out for mocking/demo purposes
    # system_prompt = (
    #     "You are an expert NPTE-PT exam tutor. Given the selected topic, generate a single NPTE-PT style multiple-choice question (MCQ) with four answer choices. "
    #     "Return ONLY a JSON object with this exact format: {\"question\": \"Your question here?\", \"choices\": [\"First choice\", \"Second choice\", \"Third choice\", \"Fourth choice\"], \"correct\": 2, \"explanations\": {0: \"Explanation for A\", 1: \"Explanation for B\", 2: \"Explanation for C\", 3: \"Explanation for D\"}, \"links\": {0: [\"https://...\"], 1: [\"https://...\"], 2: [\"https://...\"], 3: [\"https://...\"]}}. "
    #     "The 'correct' field is the 0-based index of the correct answer. 'explanations' gives a detailed explanation for each choice. 'links' gives a list of web links for further study for each choice."
    # )
    # user_prompt = f"Topic: {request.prompt}\nGenerate an MCQ as described."
    # response = client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[
    #         {"role": "system", "content": system_prompt},
    #         {"role": "user", "content": user_prompt}
    #     ],
    #     max_tokens=600,
    #     temperature=0.7,
    # )
    # content = response.choices[0].message.content.strip()
    # try:
    #     start_idx = content.find('{')
    #     end_idx = content.rfind('}') + 1
    #     if start_idx != -1 and end_idx > start_idx:
    #         json_str = content[start_idx:end_idx]
    #         mcq_data = json.loads(json_str)
    #         question = mcq_data.get("question", "")
    #         choices = mcq_data.get("choices", [])
    #         correct = mcq_data.get("correct", 0)
    #         explanations = mcq_data.get("explanations", {})
    #         links = mcq_data.get("links", {})
    #         if isinstance(choices, list) and len(choices) == 4:
    #             return MCQResponse(
    #                 question=question,
    #                 choices=choices,
    #                 correct=correct,
    #                 explanations=explanations,
    #                 links=links
    #             )
    # except Exception as e:
    #     print(f"JSON parsing failed: {e}")
    # Fallback
    # fallback_question = f"Topic: {request.prompt}\n\n{content}"
    # fallback_choices = [
    #     "A. First option",
    #     "B. Second option",
    #     "C. Third option",
    #     "D. Fourth option"
    # ]
    # fallback_explanations = {i: "No explanation available." for i in range(4)}
    # fallback_links = {i: [] for i in range(4)}
    # return MCQResponse(
    #     question=fallback_question,
    #     choices=fallback_choices,
    #     correct=0,
    #     explanations=fallback_explanations,
    #     links=fallback_links
    # )

    return MCQResponse(
        question="A 20-year-old male football player presents to the clinic with an ankle injury. The patient was tackled while his foot was stuck in the grass. He can take 5-6 steps at a time due to pain and has only mild ankle swelling. There is no tenderness over the lateral or medial malleoli.  He had a negative talar tilt test and anterior drawer but a positive Kleiger’s test. Which of the following diagnoses is MOST consistent with the patient’s symptoms?",
        choices=[
           "Ankle fracture",
           "Grade II lateral ankle sprain",
           "Grade III lateral ankle sprain",
           "High-ankle sprain"
        ],
        correct=2,
        explanations={
            0: "Option 1 is incorrect because ...",
            1: "Option 2 is incorrect because ...",
            2: "Option 3 is correct because ...",
            3: "Option 4 is incorrect because ..."
        },
        links={
            0: ["https://www.ncbi.nlm.nih.gov/books/NBK482457/"],
            1: ["https://www.ncbi.nlm.nih.gov/books/NBK279052/"],
            2: ["https://www.ncbi.nlm.nih.gov/books/NBK211546/"],
            3: ["https://www.ncbi.nlm.nih.gov/books/NBK470248/"]
        }
    )

# To run locally: uvicorn app:app --reload --host 0.0.0.0
@app.get("/")
def read_root():
    return {"message": "FastAPI backend is running!"}

@app.get("/api/random")
def get_random():
    return {"number": randint(1, 100)}
