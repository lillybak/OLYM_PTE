# NPTE RAG System

This RAG (Retrieval Augmented Generation) system enhances MCQ generation by providing the LLM with access to your NPTE materials.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd backend
uv sync  # or pip install -r requirements.txt
```

### 2. Add Your Documents
Place your NPTE materials in the `documents/` folder:
```
backend/
├── documents/
│   ├── cardiovascular_system.pdf
│   ├── musculoskeletal_notes.docx
│   ├── neuromuscular_guide.txt
│   └── ...
```

### 3. Process Documents
```bash
cd backend
python upload_documents.py
```

### 4. Start the Backend
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## 📁 Supported File Types

- **PDF** (.pdf) - Text extraction from PDFs
- **Word Documents** (.docx, .doc) - Microsoft Word files
- **Text Files** (.txt, .md) - Plain text and Markdown

## 🏷️ Automatic Topic Detection

The system automatically detects topics from filenames:

| Filename Pattern | NPTE Topic |
|------------------|------------|
| `cardiovascular_*` | Cardiovascular and pulmonary systems |
| `musculoskeletal_*` | Musculoskeletal system |
| `neuromuscular_*` | Neuromuscular and nervous systems |
| `integumentary_*` | Integumentary system |
| `metabolic_*` | Metabolic and endocrine systems |
| `gastrointestinal_*` | Gastrointestinal system |
| `genitourinary_*` | Genitourinary system |
| `lymphatic_*` | Lymphatic system |
| `system_*` | System interactions |

## 🔧 How It Works

1. **Document Processing**: Documents are split into chunks and embedded
2. **Vector Storage**: Chunks are stored in Qdrant vector database
3. **Retrieval**: When generating MCQs, relevant chunks are retrieved
4. **Enhanced Generation**: LLM uses retrieved context to generate better MCQs

## 📊 Features

- ✅ **Automatic Topic Detection** from filenames
- ✅ **Multi-format Support** (PDF, DOCX, TXT)
- ✅ **Smart Chunking** with overlap for context
- ✅ **Vector Similarity Search** for relevant content
- ✅ **Metadata Tracking** for source attribution
- ✅ **Error Handling** with fallback mechanisms

## 🎯 Usage

Once documents are uploaded, the system automatically:
- Retrieves relevant context when generating MCQs
- Enhances question quality with your materials
- Provides more accurate and detailed explanations
- Maintains source attribution for learning materials

## 🔍 API Endpoints

- `POST /api/upload_documents` - Process documents (auto-called on startup)
- `POST /api/ask` - Generate MCQs (now with RAG context)
- `POST /api/validate_answer` - Validate answers

## 🛠️ Troubleshooting

### Common Issues

1. **"RAG system not initialized"**
   - Check your OpenAI API key in `.env`
   - Ensure dependencies are installed

2. **"No documents found"**
   - Add files to `backend/documents/` folder
   - Run `python upload_documents.py`

3. **"Document processing failed"**
   - Check file format (PDF, DOCX, TXT only)
   - Ensure files are readable
   - Check file permissions

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔮 Future Enhancements

- [ ] **Web Search Integration** - Validate against current medical literature
- [ ] **Advanced Retrieval** - Hybrid dense/sparse search
- [ ] **Reranking** - Cohere reranker for better relevance
- [ ] **Evaluation** - RAGAS metrics for quality assessment
- [ ] **Tracing** - LangSmith integration for monitoring

## 📝 Example Document Structure

```
documents/
├── cardiovascular/
│   ├── cardiac_physiology.pdf
│   └── pulmonary_function.docx
├── musculoskeletal/
│   ├── joint_assessment.pdf
│   └── exercise_prescription.txt
└── neuromuscular/
    ├── neuro_examination.pdf
    └── balance_assessment.docx
```

The system will automatically categorize these by topic and use them to enhance MCQ generation! 