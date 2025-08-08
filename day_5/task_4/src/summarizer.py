"""
Summarizer Module

Handles AI-powered summarization and analysis of event reports.
Uses LangChain chains for structured analysis and query answering.
"""

import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import Document


class EventReportSummarizer:
    """Handles AI-powered summarization and analysis of event reports."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash", temperature: float = 0.1):
        """
        Initialize the event report summarizer.
        
        Args:
            model_name: Google Gemini model to use for analysis
            temperature: Temperature for model responses
        """
        self.model_name = model_name
        self.temperature = temperature
        self.llm = ChatGoogleGenerativeAI(
            model=model_name, 
            temperature=temperature,
            convert_system_message_to_human=True
        )
        self.setup_prompts()

    def setup_prompts(self):
        """Setup all the prompt templates for different analysis tasks."""
        
        self.executive_summary_prompt = PromptTemplate(
            input_variables=["content"],
            template="""Analyze the following event report and provide a comprehensive executive summary. 
            Focus on key outcomes, achievements, and strategic insights.
            
            Event Report Content:
            {content}
            
            Please provide a structured executive summary including:
            1. Event Overview
            2. Key Achievements
            3. Strategic Outcomes
            4. Notable Highlights
            
            Executive Summary:"""
        )
        
        self.query_prompt = PromptTemplate(
            input_variables=["content", "query"],
            template="""Based on the following event report content, answer the specific query.
            
            Event Report Content:
            {content}
            
            Query: {query}
            
            Please provide a detailed and accurate answer based on the event report content:"""
        )
        
        self.outcomes_prompt = PromptTemplate(
            input_variables=["content"],
            template="""Analyze the following event report and identify key outcomes and results.
            
            Event Report Content:
            {content}
            
            Please provide a detailed analysis of:
            1. Primary Outcomes
            2. Measurable Results
            3. Impact Assessment
            4. Success Metrics
            
            Key Outcomes Analysis:"""
        )
        
        self.feedback_prompt = PromptTemplate(
            input_variables=["content"],
            template="""Analyze the following event report and extract attendee feedback and satisfaction metrics.
            
            Event Report Content:
            {content}
            
            Please provide a comprehensive analysis of:
            1. Attendee Satisfaction
            2. Feedback Themes
            3. Areas for Improvement
            4. Positive Feedback Highlights
            
            Attendee Feedback Analysis:"""
        )
        
        self.recommendations_prompt = PromptTemplate(
            input_variables=["content"],
            template="""Based on the following event report, provide strategic recommendations for future events.
            
            Event Report Content:
            {content}
            
            Please provide recommendations for:
            1. Event Improvements
            2. Strategic Enhancements
            3. Best Practices to Continue
            4. Innovation Opportunities
            
            Strategic Recommendations:"""
        )

    def create_chain(self, prompt: PromptTemplate) -> LLMChain:
        """
        Create a LangChain chain with the given prompt.
        
        Args:
            prompt: Prompt template to use
            
        Returns:
            Configured LLM chain
        """
        return LLMChain(llm=self.llm, prompt=prompt)

    def _combine_documents(self, documents: List[Document]) -> str:
        """
        Combine multiple documents into a single text string.
        
        Args:
            documents: List of documents to combine
            
        Returns:
            Combined text content
        """
        return "\n\n".join([doc.page_content for doc in documents])

    def generate_executive_summary(self, documents: List[Document]) -> str:
        """
        Generate an executive summary of the event report.
        
        Args:
            documents: List of documents to analyze
            
        Returns:
            Executive summary text
        """
        content = self._combine_documents(documents)
        chain = self.create_chain(self.executive_summary_prompt)
        result = chain.run(content=content)
        return result.strip()

    def answer_query(self, documents: List[Document], query: str) -> str:
        """
        Answer a specific query about the event report.
        
        Args:
            documents: List of documents to search
            query: Specific query to answer
            
        Returns:
            Answer to the query
        """
        content = self._combine_documents(documents)
        chain = self.create_chain(self.query_prompt)
        result = chain.run(content=content, query=query)
        return result.strip()

    def analyze_outcomes(self, documents: List[Document]) -> str:
        """
        Analyze key outcomes from the event report.
        
        Args:
            documents: List of documents to analyze
            
        Returns:
            Outcomes analysis
        """
        content = self._combine_documents(documents)
        chain = self.create_chain(self.outcomes_prompt)
        result = chain.run(content=content)
        return result.strip()

    def analyze_feedback(self, documents: List[Document]) -> str:
        """
        Analyze attendee feedback from the event report.
        
        Args:
            documents: List of documents to analyze
            
        Returns:
            Feedback analysis
        """
        content = self._combine_documents(documents)
        chain = self.create_chain(self.feedback_prompt)
        result = chain.run(content=content)
        return result.strip()

    def generate_recommendations(self, documents: List[Document]) -> str:
        """
        Generate strategic recommendations based on the event report.
        
        Args:
            documents: List of documents to analyze
            
        Returns:
            Strategic recommendations
        """
        content = self._combine_documents(documents)
        chain = self.create_chain(self.recommendations_prompt)
        result = chain.run(content=content)
        return result.strip()

    def generate_comprehensive_report(self, documents: List[Document]) -> Dict[str, str]:
        """
        Generate a comprehensive analysis report.
        
        Args:
            documents: List of documents to analyze
            
        Returns:
            Dictionary containing all analysis sections
        """
        return {
            "executive_summary": self.generate_executive_summary(documents),
            "outcomes_analysis": self.analyze_outcomes(documents),
            "feedback_analysis": self.analyze_feedback(documents),
            "recommendations": self.generate_recommendations(documents)
        }
