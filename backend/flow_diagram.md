# Professor NPTE Agent with Tool-Belt

```mermaid
---
config:
  theme: redux-dark
  look: neo
---
%%  E1(("Tavily Tool: web_search <br>collect web context"))
%%  E2["PDF RAG embeddings<br>retrieve relevant chunks"]
%% end

 flowchart TB
    Z(["NPTE Topics List"])--> A["User clicks a Topic"]
    A --> B["LLM: Generate MCQ"]
    B --> C(["User selects an answer"])
    C --> D{"Reasoning LLM
            Do we need extra info?"}
    D -- Yes --> E["Decision Node
              PDF RAG? Tavily? Both?"]
    E --> E1["Tavily Tool: web_search <br>collect web context"] & E2["PDF RAG embeddings<br>retrieve relevant chunks"]
    E1 --> F["Compose Explanation
             merge RAG + web"]
    E2 --> F
    D -- No --> F
    F --> G{"Was user correct?"}
    G -- Yes --> H["Return answer + explanation + 
                   links to sources"]
    H --> END
    G -- No --> I["Return answer + explanation + 
                    learning materials:
                    web links + PDF refs"]
    I --> J["Button: 
             Continue on same topic"]
    J -- Yes --> B
    I -- "Button not clicked" --> END
    E2@{ shape: docs}
    A@{ shape: manual-input}
    J@{ shape: terminal}
     E1:::Class_17
     E1:::Class_22
     E2:::Class_13
     E2:::Class_05
     E2:::Class_08
     E2:::Class_31
     A:::Class_24
     B:::Peach
     B:::Class_10
     C:::Class_24
     D:::Class_11
     E:::Class_15
     E:::Class_16
     F:::Class_10
     G:::Class_12
     H:::Class_05
     I:::Class_23
     J:::Class_24
    classDef Peach stroke-width:1px, stroke-dasharray:none, stroke:#FBB35A, fill:#FFEFDB, color:#8F632D
    classDef Class_10 stroke:#E08300
    classDef Class_11 stroke:#7dcf0a
    classDef Class_12 stroke:#7dcf0a
    classDef Class_14 stroke:#0c65ca
    classDef Class_16 stroke:#E08300
    classDef Class_20 stroke-width:1px, stroke-dasharray: 0
    classDef Class_17 stroke:#6d0cc2
    classDef Class_13 stroke:#CB4335, stroke-width:1px, stroke-dasharray: 0
    classDef Class_23 stroke:#7dcf0a
    classDef Class_09 fill:#A8DEFF
    classDef Class_27 fill:#FFEFDB
    classDef Class_05 fill:#A9DFBF
    classDef Class_08 fill:#F1948A
    classDef Class_29 fill:#FFEFDB
    classDef Class_15 stroke-width:2px, stroke-dasharray: 0
    classDef Class_22 stroke-width:1px, stroke-dasharray: 0
    classDef Class_30 fill:#8cd1ff
    classDef Class_24 fill:#A8DEFF
    classDef Class_31 fill:#F5B7B1
    style E1 fill:#E1BEE7,color:#AA00FF
    style E2 color:#000000
    style A fill:#BBDEFB,stroke:#2962FF,color:#2962FF
    style B fill:#FFE0B2,color:#424242
    style C fill:#BBDEFB,stroke:#2962FF,color:#2962FF
    style D fill:#C8E6C9,color:#424242
    style E fill:#FFD600,color:#424242
    style F fill:#FFE0B2,color:#424242
    style G fill:#C8E6C9,color:#424242
    style H stroke:#00C853,stroke-width:2px,stroke-dasharray: 0,color:#000000
    style I fill:#FFCDD2,stroke-width:2px,stroke-dasharray: 0,stroke:#D50000,color:#424242
    style J stroke:#2962FF,color:#2962FF
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
└── Generate MCQ with A,B,C,D format, plus explanations on the choices and when the answer is incorrect provide links to learning material and an option button to continue on same subject
|
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