"""
Streamlit Web Interface for Event Report Analyzer

A user-friendly web interface for uploading PDF event reports,
asking questions, and viewing analysis results.
"""

import streamlit as st
import os
import sys
import tempfile
from pathlib import Path
from typing import Optional
import markdown
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import EventReportAnalyzerAgent


def setup_page():
    """Configure the Streamlit page."""
    st.set_page_config(
        page_title="Event Report Analyzer",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📊 Event Report Analyzer")
    st.markdown("AI-powered analysis of event reports using LangChain and Gemini 2.0 Flash")


def initialize_agent():
    """Initialize the Event Report Analyzer Agent."""
    if 'agent' not in st.session_state:
        try:
            # Check if API key is available first
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                st.error("❌ Google API key not found! Please set GOOGLE_API_KEY in your .env file.")
                return False
            
            st.session_state.agent = EventReportAnalyzerAgent(
                model_name="gemini-2.0-flash",
                temperature=0.1
            )
            st.session_state.documents_loaded = False
            st.session_state.pdf_processed = False
            return True
        except Exception as e:
            st.error(f"❌ Failed to initialize agent: {str(e)}")
            st.info("💡 Make sure your Google API key is correctly set in the .env file")
            return False
    return True


def check_api_key():
    """Check if Google API key is available."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.warning("⚠️ Google API key not found!")
        st.info("Please set your GOOGLE_API_KEY environment variable to use the AI features.")
        st.markdown("Get your API key from: https://makersuite.google.com/app/apikey")
        return False
    return True


def upload_pdf():
    """Handle PDF file upload."""
    st.header("📄 Upload Event Report")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload your event report PDF file"
    )
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Process the PDF
        if st.button("🔍 Process PDF", type="primary"):
            with st.spinner("Processing PDF..."):
                try:
                    success = st.session_state.agent.process_pdf(tmp_path)
                    if success:
                        st.session_state.pdf_processed = True
                        st.session_state.documents_loaded = True
                        st.success("✅ PDF processed successfully!")
                        
                        # Show processing stats
                        if st.session_state.agent.documents:
                            st.info(f"📊 Processed {len(st.session_state.agent.documents)} document chunks")
                    else:
                        st.error("❌ Failed to process PDF. Please check the file and try again.")
                except Exception as e:
                    st.error(f"❌ Error processing PDF: {str(e)}")
                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass
        
        return tmp_path if 'tmp_path' in locals() else None
    
    return None


def query_interface():
    """Provide interface for asking questions about the event report."""
    if not st.session_state.get('pdf_processed', False):
        st.info("📄 Please upload and process a PDF first to ask questions.")
        return
    
    st.header("❓ Ask Questions")
    
    # Predefined queries
    st.subheader("Quick Questions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Executive Summary"):
            ask_question("Generate an executive summary of the event report.")
    
    with col2:
        if st.button("🎯 Key Outcomes"):
            ask_question("What were the key outcomes and achievements?")
    
    with col3:
        if st.button("👥 Attendee Feedback"):
            ask_question("Analyze the attendee feedback and satisfaction.")
    
    # Custom query
    st.subheader("Custom Question")
    user_query = st.text_input(
        "Ask a specific question about the event:",
        placeholder="e.g., What was the attendance? What were the main challenges?"
    )
    
    if st.button("🔍 Ask Question", type="primary") and user_query:
        ask_question(user_query)


def ask_question(question: str):
    """Ask a question and display the response."""
    if not st.session_state.get('pdf_processed', False):
        st.error("Please process a PDF first.")
        return
    
    with st.spinner("Analyzing..."):
        try:
            # Add debugging information
            st.info(f"🔍 Processing question: '{question}'")
            st.info(f"📄 Documents loaded: {len(st.session_state.agent.documents) if st.session_state.agent.documents else 0}")
            
            # Use agent for all questions
            response = st.session_state.agent.run_agent(question)
            
            st.subheader("🤖 AI Response")
            st.markdown(response)
            
            # Store in session state for history
            if 'query_history' not in st.session_state:
                st.session_state.query_history = []
            
            st.session_state.query_history.append({
                'question': question,
                'response': response
            })
            
        except Exception as e:
            st.error(f"❌ Error getting response: {str(e)}")
            st.info("💡 This might be due to API issues or model limitations. Try a different question or check your API key.")


def generate_report():
    """Generate comprehensive analysis report."""
    if not st.session_state.get('pdf_processed', False):
        st.info("📄 Please upload and process a PDF first to generate a report.")
        return
    
    st.header("📊 Generate Comprehensive Report")
    
    if st.button("📋 Generate Full Report", type="primary"):
        with st.spinner("Generating comprehensive report..."):
            try:
                report = st.session_state.agent.generate_comprehensive_report()
                
                st.subheader("📊 Event Report Analysis")
                st.markdown(report)
                
                # Download option
                st.download_button(
                    label="💾 Download Report (Markdown)",
                    data=report,
                    file_name="event_report_analysis.md",
                    mime="text/markdown"
                )
                
            except Exception as e:
                st.error(f"Error generating report: {str(e)}")


def show_query_history():
    """Display query history."""
    if 'query_history' in st.session_state and st.session_state.query_history:
        st.header("📚 Query History")
        
        for i, item in enumerate(reversed(st.session_state.query_history)):
            with st.expander(f"Q: {item['question']}"):
                st.markdown(item['response'])


def interactive_mode():
    """Interactive chat mode."""
    if not st.session_state.get('pdf_processed', False):
        st.info("📄 Please upload and process a PDF first to use interactive mode.")
        return
    
    st.header("💬 Interactive Chat")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about the event report..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.agent.run_agent(prompt)
                    st.markdown(response)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})


def sidebar_info():
    """Display information in the sidebar."""
    st.sidebar.header("ℹ️ About")
    st.sidebar.markdown("""
    This tool uses:
    - **LangChain** for AI orchestration
    - **Gemini 2.0 Flash** for analysis
    - **HuggingFace embeddings** for document search
    - **Streamlit** for the web interface
    """)
    
    st.sidebar.header("🔧 Features")
    st.sidebar.markdown("""
    - 📄 PDF upload and processing
    - ❓ Question answering
    - 📊 Comprehensive reports
    - 💬 Interactive chat
    - 📚 Query history
    """)
    
    st.sidebar.header("📋 Usage")
    st.sidebar.markdown("""
    1. Upload your event report PDF
    2. Process the document
    3. Ask questions or generate reports
    4. Use interactive chat for detailed analysis
    """)
    
    # Status indicators
    st.sidebar.header("📊 Status")
    if st.session_state.get('pdf_processed', False):
        st.sidebar.success("✅ PDF Processed")
    else:
        st.sidebar.info("📄 No PDF processed")
    
    if check_api_key():
        st.sidebar.success("🔑 API Key Available")
    else:
        st.sidebar.error("❌ API Key Missing")


def main():
    """Main Streamlit application."""
    setup_page()
    
    # Initialize agent
    if not initialize_agent():
        st.error("❌ Failed to initialize the analyzer. Please check your setup.")
        st.info("💡 Make sure you have:")
        st.info("1. Set GOOGLE_API_KEY in your .env file")
        st.info("2. Installed all required dependencies")
        st.info("3. Have a valid Google API key")
        return
    
    # Check API key
    api_key_available = check_api_key()
    
    # Sidebar
    sidebar_info()
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Upload & Process", 
        "❓ Ask Questions", 
        "📊 Generate Report",
        "💬 Interactive Chat"
    ])
    
    with tab1:
        upload_pdf()
    
    with tab2:
        query_interface()
        show_query_history()
    
    with tab3:
        generate_report()
    
    with tab4:
        interactive_mode()
    
    # Footer
    st.markdown("---")
    st.markdown("*Powered by LangChain and Google Gemini 2.0 Flash*")


if __name__ == "__main__":
    main()
