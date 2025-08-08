1. Frontend (frontend-vite/ directory)  
This is your React app (what the user sees and interacts with).
It runs in the browser and is served by Vite during development.
It does not contain or run any Python code.
It communicates with the backend by making HTTP requests (using fetch or axios).


2. Backend (backend/app.py)  
This is your FastAPI app (Python code).
It runs on your server (or locally, via uvicorn app:app --reload --host 0.0.0.0 --port 8000).
It handles requests from the frontend, generates MCQs, checks answers, and returns data as JSON.


### How do they communicate?
* Frontend:
Makes a request like:
  ```tsx
  fetch('http://localhost:8000/api/ask', { ... })
  ```
* Backend (app.py):  
Receives the request, processes it, and sends back a response (e.g., a new MCQ).


###Summary Table  

| Part      | Directory         | Language    | Runs where?         | Role                        |
|-----------|-------------------|-------------|---------------------|-----------------------------|
| Frontend  | frontend-vite/    | TypeScript  | Browser (Vite dev)  | User interface, HTTP client |
| Backend   | backend/app.py    | Python      | Server/localhost    | Logic, LLM, API endpoints   |
--------------------------------------------------------------------------------------------------

You never copy or move app.py into your frontend.
You just make sure it’s running, and your frontend will “talk” to it by making HTTP requests

  flowchart TD
  A["User in Browser"]
  B["React App (frontend-vite)"]
  C["FastAPI Backend (app.py)"]
  D["LLM, LangChain, Qdrant, etc."]

  A -->|Interacts with| B
  B -->|Sends HTTP Request| C
  C -->|Returns JSON: MCQ, feedback, etc.| B
  C -->|Uses| D
  D -->|Provides data/results| C

