import os
import re
from typing import List
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.retrievers import BaseRetriever

# Streamlit imports
import streamlit as st
import time

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ------------------------------
# 1. Load & Chunk Wikipedia File
# ------------------------------
def load_and_chunk_wikipedia(file_path: str) -> List[Document]:
    """Load and chunk the Wikipedia file using proper text splitting"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Clean up the content
    content = re.sub(r'\n\s*\n', '\n\n', content)
    content = re.sub(r' +', ' ', content)
    
    # Split content into sections based on headers
    sections = []
    lines = content.split('\n')
    current_section = []
    current_title = "Robotics"
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for headers - this file uses plain text headers
        if (line in ["Robotics aspects", "Applied robotics", "Mechanical robotics areas", 
                     "Power source", "Actuation", "Electric motors", "Linear actuators", 
                     "Series elastic actuators", "Control robotics areas", "Sensing", 
                     "Manipulation", "Locomotion", "Environmental interaction and navigation",
                     "Human-robot interaction", "Learning", "Programming", "Autonomy", 
                     "Research and development", "Education and training", "Employment",
                     "Occupational safety and health", "History", "Future development and trends",
                     "See also", "References", "Further reading", "External links"]):
            # Save previous section
            if current_section:
                section_text = '\n'.join(current_section).strip()
                if section_text and len(section_text) > 100:
                    sections.append((current_title, section_text))
            current_title = line
            current_section = []
        else:
            current_section.append(line)
    
    # Add the last section
    if current_section:
        section_text = '\n'.join(current_section).strip()
        if section_text and len(section_text) > 100:
            sections.append((current_title, section_text))
    
    # Now process each section and create meaningful chunks
    documents = []
    for title, section_text in sections:
        # Skip reference sections
        if any(keyword in title.lower() for keyword in ['references', 'external links', 'further reading', 'notes', 'see also']):
            continue
            
        # Clean the section text
        section_text = re.sub(r'\[\d+\]', '', section_text)  # Remove citation numbers
        section_text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', section_text)  # Remove URLs
        
        # Split section into paragraphs
        paragraphs = section_text.split('\n\n')
        
        # Create chunks from paragraphs
        current_chunk = []
        chunk_size = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph or len(paragraph) < 50:
                continue
                
            # Skip paragraphs that are mostly URLs or references
            if 'http' in paragraph.lower() or paragraph.count('[') > 3:
                continue
                
            # If adding this paragraph would make chunk too large, save current chunk
            if chunk_size + len(paragraph) > 1500 and current_chunk:
                chunk_text = '\n\n'.join(current_chunk)
                if len(chunk_text) > 200:  # Only add substantial chunks
                    metadata = {"title": title, "section": title}
                    documents.append(Document(page_content=chunk_text, metadata=metadata))
                current_chunk = [paragraph]
                chunk_size = len(paragraph)
            else:
                current_chunk.append(paragraph)
                chunk_size += len(paragraph)
        
        # Add the last chunk from this section
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            if len(chunk_text) > 200:
                metadata = {"title": title, "section": title}
                documents.append(Document(page_content=chunk_text, metadata=metadata))
    
    return documents

# ----------------------------------------
# 2. Embedding + ChromaDB Vector Store
# ----------------------------------------
def embed_documents(docs: List[Document], persist_directory="chroma_db") -> Chroma:
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = Chroma.from_documents(documents=docs, embedding=embedding_model, persist_directory=persist_directory)
    # Note: persist() is no longer needed in newer Chroma versions
    return vectordb

def load_vectorstore(persist_directory="chroma_db") -> Chroma:
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return Chroma(persist_directory=persist_directory, embedding_function=embedding_model)

# ------------------------------
# 3. Prompt Template for QA
# ------------------------------
qa_prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "You are a helpful AI educator specializing in robotics. Your task is to answer questions based on the provided context from a Wikipedia article about robotics.\n\n"
        "Instructions:\n"
        "- Use ONLY the information provided in the context to answer the question\n"
        "- If the context contains relevant information, provide a comprehensive and accurate answer\n"
        "- If the context doesn't contain enough information to answer the question, say 'I don't have enough information to answer this question.'\n"
        "- Be specific and detailed in your answers\n"
        "- Include relevant examples and technical details when available\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer:"
    )
)

# ------------------------------
# 4. Gemini LLM Setup
# ------------------------------
def setup_llm():
    """Setup the LLM with proper error handling for credentials"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n[ERROR] Google API key not found!")
        return None
    
    try:
        return ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)
    except Exception as e:
        print(f"\n[ERROR] Failed to initialize Google Generative AI: {e}")
        print("Please check your API key and internet connection.")
        return None

llm = setup_llm()

# ------------------------------
# 5. Define Tools for Agent
# ------------------------------
def create_tools(retriever: BaseRetriever):
    def custom_qa_tool(query: str) -> str:
        try:
            # Get relevant documents
            docs = retriever.invoke(query)
            
            if not docs:
                return "I don't have enough information to answer this question."
            
            # Combine context from all relevant documents
            context_parts = []
            for doc in docs:
                context_parts.append(doc.page_content)
            
            context = "\n\n".join(context_parts)
            
            # Create the prompt
            prompt = qa_prompt_template.format(context=context, question=query)
            
            # Get response from LLM
            response = llm.invoke(prompt)
            
            # Add citations
            citations = []
            for doc in docs:
                title = doc.metadata.get('title', 'Unknown')
                citations.append(f"From '{title}'")
            
            citation_text = " ".join(citations)
            
            # Return the response with citations
            return f"{response.content}\n\nCitations: {citation_text}"
            
        except Exception as e:
            return f"Error processing query: {str(e)}"

    return [
        Tool(
            name="Wikipedia QA Tool",
            func=custom_qa_tool,
            description="Answer questions about robotics using Wikipedia articles with detailed explanations and citations"
        )
    ]

# ------------------------------
# 6. LangChain Agent Setup
# ------------------------------
def create_agent(tools):
    return initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

# ------------------------------
# 8. Streamlit UI Functions
# ------------------------------
def initialize_session_state():
    """Initialize Streamlit session state"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'agent_initialized' not in st.session_state:
        st.session_state.agent_initialized = False
    if 'vectordb' not in st.session_state:
        st.session_state.vectordb = None
    if 'agent' not in st.session_state:
        st.session_state.agent = None

def setup_rag_system():
    """Setup the RAG system with proper error handling"""
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to the task_2 directory
        project_dir = os.path.dirname(script_dir)
        
        FILE_PATH = os.path.join(project_dir, "data", "wikipedia_robotics.txt")
        DB_PATH = os.path.join(project_dir, "data", "chroma_db")

        # Check if the data file exists
        if not os.path.exists(FILE_PATH):
            st.error(f"Data file not found: {FILE_PATH}")
            return False

        # Check if LLM is available
        if llm is None:
            st.error("Cannot proceed without a working LLM. Please set up your Google API key.")
            return False

        # Create or load vector database
        if not os.path.exists(DB_PATH):
            with st.spinner("Embedding documents and creating vector store..."):
                documents = load_and_chunk_wikipedia(FILE_PATH)
                st.info(f"Created {len(documents)} document chunks")
                embed_documents(documents, DB_PATH)
                st.success("Vector store created successfully")

        # Load vector store and create agent
        vectordb = load_vectorstore(DB_PATH)
        retriever = vectordb.as_retriever(search_kwargs={"k": 5})
        tools = create_tools(retriever)
        agent = create_agent(tools)

        # Store in session state
        st.session_state.vectordb = vectordb
        st.session_state.agent = agent
        st.session_state.agent_initialized = True
        
        return True
        
    except Exception as e:
        st.error(f"Error setting up RAG system: {str(e)}")
        return False

def streamlit_ui():
    """Main Streamlit UI"""
    st.set_page_config(
        page_title="Robotics RAG System",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Robotics RAG System")
    st.markdown("Ask questions about robotics using our Wikipedia-based knowledge system!")
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar for system info
    with st.sidebar:
        st.header("System Information")
        st.markdown("""
        This system uses:
        - **RAG (Retrieval-Augmented Generation)**
        - **Wikipedia Robotics Article**
        - **Chroma Vector Database**
        - **Google Gemini LLM**
        """)
        
        if st.button("🔄 Rebuild Vector Database"):
            if os.path.exists("data/chroma_db"):
                import shutil
                shutil.rmtree("data/chroma_db")
                st.success("Old database deleted!")
            st.session_state.agent_initialized = False
            st.rerun()
    
    # Initialize RAG system
    if not st.session_state.agent_initialized:
        with st.spinner("Initializing RAG system..."):
            if setup_rag_system():
                st.success("RAG system initialized successfully!")
            else:
                st.error("Failed to initialize RAG system!")
                return
    
    # Chat interface
    st.header("💬 Chat with Robotics Expert")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about robotics..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                with st.spinner("Thinking..."):
                    # Get response from agent
                    response = st.session_state.agent.invoke({"input": prompt})
                    answer = response['output']
                
                # Display response
                message_placeholder.markdown(answer)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                error_msg = f"Error getting response: {str(e)}"
                message_placeholder.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ------------------------------
# 7. Main Loop (Streamlit Only)
# ------------------------------
if __name__ == "__main__":
    streamlit_ui()
