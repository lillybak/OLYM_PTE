# NPTE Agent with Simplified Tool-Belt

```mermaid
flowchart TD
    Human[Human]
    Agent[Agent with Reasoning]
    WebTool[Tavily Tool]
    RAGTool[RAG Tool<br/>Qdrant Embeddings]
    
    Human -->|"1. Select Topic"| Agent
    Agent -->|"2. Use RAG Tool"| RAGTool
    Agent -->|"3. Use Web Tool"| WebTool
    RAGTool -->|"4. Return PDF Chunks"| Agent
    WebTool -->|"5. Return Web Results"| Agent
    Agent -->|"6. Generate QA"| Human
    Human -->|"7. Send Answer"| Agent
    Agent -->|"8. Check & Explain"| Human
    Human -->|"9. Continue/Change/Quit"| Agent
```

## Simplified Agent with Tool-Belt

### **Agent's Tool-Belt:**
- **RAG Tool** - Qdrant embeddings (your PDFs)
- **Web Tool** - Tavily for current medical literature
- **General Knowledge** - Built-in LLM knowledge

### **Agent's Process:**
```
For each request:
├── Use RAG tool (get PDF context)
├── Use web tool (get current literature)
├── Combine contexts
└── Generate MCQ with A,B,C,D format
```

### **Flow:**
1. **Human** selects topic → **Agent**
2. **Agent** uses RAG tool → Gets PDF context
3. **Agent** uses web tool → Gets current literature
4. **Agent** combines contexts → Generates MCQ
5. **Agent** generates QA → **Human**
6. **Human** sends answer → **Agent**
7. **Agent** checks & explains → **Human**
8. **Human** decides next action → **Agent**

### **Key Features:**
- **Simple tool usage** - RAG + Web for all topics
- **A,B,C,D format** - Standard MCQ format
- **Combined contexts** - PDF + current literature
- **Human control** - All decisions

---

## Future Enhancements:

### **When you have performance data:**
- **Track retrieval performance** per topic
- **Compare RAG vs Cohere** results
- **Add intelligent tool selection** based on data
- **Implement hybrid retrieval** for complex topics

### **For now:**
- **Use RAG for all topics** (simpler, works well)
- **Add web search** for current content
- **Focus on MCQ quality** with A,B,C,D format 