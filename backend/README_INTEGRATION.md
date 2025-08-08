# NPTE Agent System Integration

## 🎯 **What We've Built:**

### **Agent with Tool-Belt Architecture:**
- **Agent** - LLM with reasoning capabilities
- **RAG Tool** - Access to your PDF embeddings in Qdrant
- **Web Tool** - Tavily for current medical literature (simulated)
- **General Knowledge** - Built-in LLM knowledge

### **3-Node System:**
```
Human ↔ Agent ↔ Tools (RAG + Web)
```

## 🚀 **Quick Start:**

### **1. Install Dependencies:**
```bash
cd backend
uv sync  # or pip install -r requirements.txt
```

### **2. Add Your PDFs:**
```bash
# Place your PDFs in the documents folder
cp your_pdfs/*.pdf documents/
```

### **3. Process Documents:**
```bash
python upload_documents.py
```

### **4. Test the Agent:**
```bash
python test_agent.py
```

### **5. Start Backend:**
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### **6. Start Frontend:**
```bash
cd ../frontend-vite
npm run dev
```

## 🧪 **Testing:**

### **Test Agent System:**
```bash
python test_agent.py
```

### **Test Backend API:**
```bash
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Cardiovascular and pulmonary systems"}'
```

### **Test Frontend:**
- Open http://localhost:5173
- Select a topic
- Answer questions
- See adaptive learning in action

## 🔧 **How It Works:**

### **Agent Decision Process:**
1. **Human** selects topic
2. **Agent** decides which tools to use:
   - General knowledge (fastest)
   - RAG tool (PDF content needed)
   - Web tool (current protocols needed)
   - Combine tools (complex scenarios)
3. **Agent** generates MCQ
4. **Human** answers
5. **Agent** validates and provides feedback
6. **Human** decides next action

### **Key Features:**
- ✅ **Tool-belt architecture** - Agent chooses tools intelligently
- ✅ **RAG integration** - Uses your PDF research papers
- ✅ **Web search** - Gets current medical literature
- ✅ **Adaptive learning** - Adjusts based on performance
- ✅ **Medical safety** - Grounded in real sources

## 📊 **Next Steps:**

### **Phase 1: Basic Integration (Current)**
- ✅ Agent with RAG tool
- ✅ MCQ generation and validation
- ✅ Frontend integration

### **Phase 2: Enhanced Features**
- [ ] Real Tavily web search integration
- [ ] Advanced RAG with reranking
- [ ] LangChain/LangGraph orchestration
- [ ] RAGAS evaluation

### **Phase 3: Production Features**
- [ ] User progress tracking
- [ ] Mastery level assessment
- [ ] Personalized learning paths
- [ ] Performance analytics

## 🎯 **Ready to Test!**

Your agent system is now integrated and ready to generate NPTE MCQs using your research papers and current medical knowledge! 