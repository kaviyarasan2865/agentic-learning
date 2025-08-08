"""
Event Report Analyzer Agent

Main LangChain agent that orchestrates PDF processing, vector storage,
and AI analysis for event report processing.
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from langchain.agents import initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import Document
from langchain.tools import BaseTool, tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from pdf_processor import PDFProcessor
from vector_store import VectorStoreManager
from summarizer import EventReportSummarizer


class EventReportAnalyzerAgent:
    """Main agent for analyzing event reports using LangChain."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash", temperature: float = 0.1):
        """
        Initialize the Event Report Analyzer Agent.
        
        Args:
            model_name: Google Gemini model to use
            temperature: Temperature for model responses
        """
        self.model_name = model_name
        self.temperature = temperature
        self.llm = ChatGoogleGenerativeAI(
            model=model_name, 
            temperature=temperature,
            convert_system_message_to_human=True
        )
        self.pdf_processor = PDFProcessor()
        self.vector_store_manager = VectorStoreManager()
        self.summarizer = EventReportSummarizer(model_name=model_name, temperature=temperature)
        self.documents = None
        self.vector_store = None
        self.agent = None
        self.tools = None

    def setup_tools(self) -> List[BaseTool]:
        """Setup the tools available to the agent."""
        
        @tool
        def search_event_details(query: str) -> str:
            """Search for specific details in the event report and return the found information."""
            if not hasattr(self, 'documents') or not self.documents:
                return "No documents loaded. Please process a PDF first."
            
            try:
                results = self.vector_store_manager.similarity_search(query, k=5)
                if results:
                    content = "\n\n".join([doc.page_content for doc in results])
                    return f"Here is the relevant information found for '{query}':\n\n{content}"
                else:
                    return f"No relevant information found for '{query}' in the event report."
            except Exception as e:
                return f"Error searching event details: {str(e)}"

        @tool
        def generate_summary() -> str:
            """Generate an executive summary of the event report."""
            if not hasattr(self, 'documents') or not self.documents:
                return "No documents loaded. Please process a PDF first."
            
            try:
                summary = self.summarizer.generate_executive_summary(self.documents)
                return summary
            except Exception as e:
                return f"Error generating summary: {str(e)}"

        @tool
        def analyze_outcomes() -> str:
            """Analyze key outcomes from the event report."""
            if not hasattr(self, 'documents') or not self.documents:
                return "No documents loaded. Please process a PDF first."
            
            try:
                outcomes = self.summarizer.analyze_outcomes(self.documents)
                return outcomes
            except Exception as e:
                return f"Error analyzing outcomes: {str(e)}"

        @tool
        def analyze_feedback() -> str:
            """Analyze attendee feedback from the event report."""
            if not hasattr(self, 'documents') or not self.documents:
                return "No documents loaded. Please process a PDF first."
            
            try:
                feedback = self.summarizer.analyze_feedback(self.documents)
                return feedback
            except Exception as e:
                return f"Error analyzing feedback: {str(e)}"

        @tool
        def answer_specific_question(question: str) -> str:
            """Answer a specific question about the event report and provide a detailed response."""
            if not hasattr(self, 'documents') or not self.documents:
                return "No documents loaded. Please process a PDF first."
            
            try:
                answer = self.summarizer.answer_query(self.documents, question)
                return f"Answer to '{question}':\n\n{answer}"
            except Exception as e:
                return f"Error answering question: {str(e)}"

        @tool
        def get_vector_store_stats() -> str:
            """Get statistics about the vector store."""
            try:
                stats = self.vector_store_manager.get_vector_store_stats()
                return f"Vector store statistics: {stats}"
            except Exception as e:
                return f"Error getting vector store stats: {str(e)}"

        return [
            search_event_details,
            generate_summary,
            analyze_outcomes,
            analyze_feedback,
            answer_specific_question,
            get_vector_store_stats
        ]

    def initialize_agent(self):
        """Initialize the agent with tools using initialize_agent."""
        self.tools = self.setup_tools()
        
        # Use initialize_agent instead of AgentExecutor
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
        return True

    def process_pdf(self, pdf_path: str) -> bool:
        """
        Process a PDF file and prepare it for analysis.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            True if processing was successful
        """
        try:
            print(f"Processing PDF: {pdf_path}")
            self.documents = self.pdf_processor.process_pdf(pdf_path)
            print(f"Processed {len(self.documents)} document chunks")
            
            self.vector_store = self.vector_store_manager.create_vector_store(self.documents)
            print("Vector store created successfully")
            
            self.initialize_agent()
            print("Agent initialization complete")
            
            return True
            
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            return False

    def run_agent(self, query: str) -> str:
        """
        Run the agent with a specific query.
        
        Args:
            query: Query to process
            
        Returns:
            Agent response
        """
        if not self.agent:
            return "Agent not initialized. Please process a PDF first."
        
        if not self.documents:
            return "No documents loaded. Please process a PDF first."
        
        try:
            # Create a more specific prompt that forces tool usage
            if "highlight" in query.lower() or "plenary" in query.lower():
                enhanced_query = f"Search for information about '{query}' in the event report and provide a detailed analysis."
            elif "summary" in query.lower():
                enhanced_query = f"Generate an executive summary of the event report."
            elif "outcome" in query.lower():
                enhanced_query = f"Analyze the key outcomes from the event report."
            elif "feedback" in query.lower():
                enhanced_query = f"Analyze the attendee feedback from the event report."
            else:
                enhanced_query = f"Answer this specific question about the event report: '{query}'"
            
            result = self.agent.run(enhanced_query)
            return result
        except Exception as e:
            return f"Error running agent: {str(e)}"

    def call_tool_directly(self, tool_name: str, **kwargs) -> str:
        """
        Call a tool directly without going through the agent executor.
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Arguments for the tool
            
        Returns:
            Tool response
        """
        if not self.tools:
            return "Tools not initialized. Please call initialize_agent() first."
        
        # Find the tool by name
        tool_map = {tool.name: tool for tool in self.tools}
        
        if tool_name not in tool_map:
            return f"Tool '{tool_name}' not found. Available tools: {list(tool_map.keys())}"
        
        try:
            tool = tool_map[tool_name]
            result = tool.invoke(kwargs)
            return result
        except Exception as e:
            return f"Error calling tool '{tool_name}': {str(e)}"

    def search_plenary_highlights(self) -> str:
        """
        Directly search for highlights from plenary sessions.
        
        Returns:
            Highlights from plenary sessions
        """
        if not self.documents:
            return "No documents loaded. Please process a PDF first."
        
        try:
            # Search for plenary session content
            results = self.vector_store_manager.similarity_search("plenary sessions highlights", k=5)
            if results:
                content = "\n\n".join([doc.page_content for doc in results])
                return f"## Highlights from Plenary Sessions\n\n{content}"
            else:
                # Try alternative search terms
                results = self.vector_store_manager.similarity_search("plenary", k=5)
                if results:
                    content = "\n\n".join([doc.page_content for doc in results])
                    return f"## Plenary Session Information\n\n{content}"
                else:
                    return "No information about plenary sessions found in the event report."
        except Exception as e:
            return f"Error searching for plenary highlights: {str(e)}"

    def generate_comprehensive_report(self, output_path: Optional[str] = None) -> str:
        """
        Generate a comprehensive analysis report.
        
        Args:
            output_path: Optional path to save the report
            
        Returns:
            Generated report content
        """
        if not self.documents:
            return "No documents loaded. Please process a PDF first."
        
        try:
            report = self.summarizer.generate_comprehensive_report(self.documents)
            
            # Format as markdown
            markdown_content = f"""# Event Report Analysis

## Executive Summary
{report['executive_summary']}

## Key Outcomes Analysis
{report['outcomes_analysis']}

## Attendee Feedback Analysis
{report['feedback_analysis']}

## Strategic Recommendations
{report['recommendations']}

---
*Report generated using Gemini 2.0 Flash model*
"""
            
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                print(f"Report saved to: {output_path}")
            
            return markdown_content
            
        except Exception as e:
            return f"Error generating comprehensive report: {str(e)}"

    def interactive_mode(self):
        """Run the agent in interactive mode."""
        print("Event Report Analyzer - Interactive Mode")
        print("Type 'quit' to exit")
        print("-" * 50)
        
        while True:
            try:
                query = input("\nEnter your query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if not query:
                    continue
                
                response = self.run_agent(query)
                print(f"\nResponse: {response}")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
