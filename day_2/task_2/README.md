# 🤖 Robotics RAG System

A Retrieval-Augmented Generation (RAG) system for answering questions about robotics using Wikipedia data.

---

## 📋 Problem Statement / Summary

### Task Overview
Build a RAG QA system using Wikipedia content (exported as TXT) on a specific domain - robotics. The system must demonstrate the complete RAG pipeline from document processing to answer generation.

### Key Requirements
- **Chunk by subtopic or header**: Implement intelligent section-based chunking of Wikipedia content
- **Embed by hierarchy**: Preserve hierarchical structure (H1, H2, H3) through metadata
- **LLM for educational QA**: Use advanced language models for comprehensive answer generation
- **Cite article title and section name**: Provide proper source attribution and citations

### Sample Questions to Test
- Who invented the first robot?
- What is SLAM in robotics?
- What are the three main aspects of robotics?
- How do electric motors work in robots?
- What are the applications of robotics in manufacturing?

### Solution Approach
This project implements a complete RAG system that:
1. **Processes** Wikipedia robotics article into structured chunks
2. **Embeds** content using sentence transformers for semantic search
3. **Retrieves** relevant information using vector similarity
4. **Generates** educational answers with proper citations
5. **Provides** both web and command-line interfaces

---

## 🛠️ Tools/Libraries Used

### Core Framework
- **LangChain**: Main framework for RAG pipeline orchestration
- **LangChain Community**: Community components and integrations
- **LangChain Core**: Core abstractions and interfaces
- **LangChain Text Splitters**: Document chunking utilities

### Vector Database & Embeddings
- **ChromaDB**: Vector database for storing and retrieving embeddings
- **Sentence Transformers**: HuggingFace embeddings for semantic search
- **HuggingFace Embeddings**: Integration with HuggingFace models

### Language Model
- **Google Generative AI**: Gemini 2.0 Flash for answer generation
- **LangChain Google GenAI**: LangChain integration with Google AI

### Web Interface
- **Streamlit**: Modern web application framework
- **Streamlit Chat**: Chat interface components

### Development & Environment
- **Python-dotenv**: Environment variable management
- **Python 3.8+**: Runtime environment

### Data Processing
- **Regular Expressions**: Text cleaning and processing
- **File I/O**: Document loading and management

---

## 🚀 Features

- **RAG-based Q&A:** Ask questions about robotics and get detailed, context-aware answers.
- **Wikipedia Knowledge Base:** Uses a comprehensive Wikipedia article on robotics as its source.
- **Smart Retrieval:** Finds and cites the most relevant information from the knowledge base.
- **Multiple Interfaces:** Both CLI and modern Streamlit web interface.
- **Accurate Answers:** Provides citations and detailed explanations, referencing article sections.

---

## 🏗️ System Architecture

```
┌──────────────┐    ┌──────────────┐    ┌────────────────────┐
│   User Query │──▶│  RAG System  │──▶│ Wikipedia Knowledge │
│              │    │              │    │      Base          │
└──────────────┘    └──────────────┘    └────────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Vector Store │
                    │  (ChromaDB)  │
                    └──────────────┘
```

- **Document Processing:** Section-based chunking, metadata preservation, and content cleaning.
- **Vector Database:** Embeddings via HuggingFace sentence-transformers, stored in ChromaDB.
- **RAG Pipeline:** Top-k semantic retrieval, Gemini LLM for answer synthesis, and citation generation.
- **User Interface:** Streamlit web app and CLI.

---

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd day_2/task_2
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Google API Key**
   - Get a Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a `.env` file in the project root:
     ```
     GOOGLE_API_KEY=your_api_key_here
     ```

---

## 🖥️ Usage

### Option 1: Streamlit Web Interface (Recommended)

1. **Launch the web interface**
   ```bash
   streamlit run src/main.py
   ```

2. **Open your browser** to [http://localhost:8501](http://localhost:8501)

3. **Features:**
   - Modern chat interface
   - Chat history
   - Database rebuild option
   - System information sidebar

---

### Option 2: Command Line Interface

1. **Run the CLI version**
   ```bash
   python src/main.py
   ```

2. **Features:**
   - Terminal-based interaction
   - Fast responses
   - Debug information

---

## ❓ Example Questions

Try these questions to test the system:

- Who invented the first robot?
- What is SLAM in robotics?
- What are the three main aspects of robotics?
- What types of sensors are used in robots?
- How do electric motors work in robots?
- What are the applications of robotics in manufacturing?

---

## 🧩 System Components

### 1. Document Processing
- **Chunking Strategy:** Section-based, ~1500 characters per chunk, preserves hierarchy.
- **Content Cleaning:** Removes citations and URLs.
- **Metadata:** Preserves section titles and structure.

### 2. Vector Database
- **Embeddings:** HuggingFace sentence-transformers (`all-MiniLM-L6-v2`)
- **Storage:** ChromaDB for efficient retrieval
- **Indexing:** Semantic search (cosine similarity)

### 3. RAG Pipeline
- **Retrieval:** Top-5 most relevant chunks
- **Generation:** Google Gemini LLM for answer synthesis
- **Citations:** Provides source section for every answer

### 4. User Interface
- **Streamlit:** Modern web interface
- **CLI:** Command-line alternative
- **Error Handling:** Graceful error management

---

## 🛠️ Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **API Key Issues**
   - Ensure `.env` file exists with `GOOGLE_API_KEY`
   - Check API key validity

3. **Vector Database Issues**
   - Delete `data/chroma_db` folder
   - Restart the application

4. **Memory Issues**
   - Reduce chunk size in `load_and_chunk_wikipedia()`
   - Use a smaller embedding model

### Performance Tips

- **First Run:** May take time to create embeddings
- **Subsequent Runs:** Fast startup with cached database
- **Memory:** Ensure sufficient RAM for embeddings

---

## 📁 File Structure

```
day_2/task_2/
├── src/
│   └── main.py              # Core RAG system
├── data/
│   ├── wikipedia_robotics.txt  # Knowledge base
│   └── chroma_db/             # Vector database
├── requirements.txt           # Dependencies
├── .gitignore                # Git ignore patterns
└── README.md                 # This file
```

---

## 🧑‍💻 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📜 License

This project is for educational purposes.

---

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Review error messages
3. Ensure all dependencies are installed
4. Verify API key configuration

---

*For more technical details, see the `docs/` directory.*
