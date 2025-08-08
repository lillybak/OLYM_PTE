import os
import re
import uvicorn
import requests
from typing import Any, Dict
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from llama_cpp import Llama  # llama-cpp-python bindings :contentReference[oaicite:2]{index=2}

# 1. Initialize local LLM
llm = Llama(
    model_path=os.getenv("MODEL_PATH", "CodeLlama-13B-Instruct.gguf"),
    n_ctx=65536,
    use_mlock=True,
    low_vram=False,
    seed=1234,
)

# 2. FastAPI app
api = FastAPI()
api.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

class Message(BaseModel):
    question: str
    history: list[Dict[str, Any]] = []

class AgentTool:
    """Simple tool definitions that return Observations."""

    def retriever(self, subject: str) -> str:
        # >>> your subject-based embedding search
        # e.g. call your local retriever library
        # return plain FAQ-like filler for now
        return f"Retrieved Q&A snippets for subject '{subject}' …"

    def search_web(self, query: str) -> str:
        # >>> use Serper, Wiki, or simple requests
        resp = requests.get(
            "https://api.serper.dev/search",
            headers={"X-API-KEY": os.getenv("SERPER_KEY")},
            params={"q": query}
        )
        return resp.json().get("snippet") if resp.ok else "Search failed"

tools = AgentTool()

# 3. ReAct prompt template
PROMPT_TEMPLATE = """
You are a quiz coach. Use step‑by‑step reasoning and only one action (tool call) at a time in JSON format.

{{history}}

Student question: {question}

Thought:
Action:
Only use one of: "retriever" or "search_web"
Action input: ({"tool": "...", "question": "..."} in JSON)
Observation:
Final Answer:
"""

# 4. Agent loop
@app.post("/api/agent")
def agent_endpoint(msg: Message):
    history_text = ""
    for turn in msg.history:
        history_text += f"{turn['role']}: {turn['text']}\n"
    prompt = PROMPT_TEMPLATE.format(history=history_text, question=msg.question.strip())

    result_text = ""
    for step in range(8):  # max iterations
        # call LLM
        completion = llm(
            prompt=prompt,
            streaming=False,
            temperature=0.2,
            max_tokens=1024,
        )
        result = completion["choices"][0]["text"].strip()
        prompt += result + "\n"

        # parse for Action
        m = re.search(r'Action input:\s*(\{.*?\})', result, re.S)
        if m:
            json_part = m.group(1)
            try:
                j = eval(json_part)
            except Exception:
                return {"error": "Invalid JSON from model", "raw": result}
            tool = j.get("tool")
            arg = j.get("question") or j.get("subject") or ""
            obs = getattr(tools, tool)(arg)
            # inject into prompt
            prompt += f"Observation: {obs}\n"
        else:
            # No action → Final Answer
            final_m = re.search(r'Final Answer:\s*(.*)', result, re.S)
            final_answer = final_m.group(1).strip() if final_m else result
            return {"answer": final_answer, "trace": result}

    return {"answer": "(no final answer)", "trace": result_text}

if __name__ == "__main__":
    print("Starting local agent on https://127.0.0.1:8000")
    uvicorn.run(api, host="127.0.0.1", port=8000)

