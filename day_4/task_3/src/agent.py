"""
Astronomy Agent - ReAct Pattern Implementation
Uses LangChain's initialize_agent with Gemini LLM for reasoning and web scraping for actions.
"""

import os
from typing import List, Dict, Any
from langchain.agents import initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool
from web_scraper import WebScraper
from question_generator import QuestionGenerator

class AstronomyAgent:
    """
    ReAct Agent for Astronomy Fact Finding
    Implements reasoning (question generation) and acting (web scraping) pattern.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the Astronomy Agent.
        
        Args:
            api_key (str): Google Gemini API key
        """
        self.api_key = api_key
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=0.7
        )
        
        # Initialize components
        self.web_scraper = WebScraper()
        self.question_generator = QuestionGenerator(self.llm)
        
        # Create tools for the agent
        self.tools = self._create_tools()
        
        # Initialize the ReAct agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the ReAct agent."""
        
        def search_astronomy_info(query: str) -> str:
            """
            Search for astronomy information on the web.
            
            Args:
                query (str): Search query
                
            Returns:
                str: Retrieved information
            """
            try:
                return self.web_scraper.search_and_scrape(query)
            except Exception as e:
                return f"Error searching for information: {str(e)}"
        
        def search_wikipedia(query: str) -> str:
            """
            Search Wikipedia for astronomy information.
            
            Args:
                query (str): Search query
                
            Returns:
                str: Retrieved information from Wikipedia
            """
            try:
                return self.web_scraper.search_wikipedia(query)
            except Exception as e:
                return f"Error searching Wikipedia: {str(e)}"
        
        def search_nasa_info(query: str) -> str:
            """
            Search NASA websites for astronomy information.
            
            Args:
                query (str): Search query
                
            Returns:
                str: Retrieved information from NASA sources
            """
            try:
                return self.web_scraper.search_nasa_sources(query)
            except Exception as e:
                return f"Error searching NASA sources: {str(e)}"
        
        tools = [
            Tool(
                name="search_astronomy_info",
                func=search_astronomy_info,
                description="Search for general astronomy information on the web. Use this for finding facts, definitions, and explanations about astronomical phenomena."
            ),
            Tool(
                name="search_wikipedia",
                func=search_wikipedia,
                description="Search Wikipedia for detailed information about astronomy topics. Use this for comprehensive explanations and historical context."
            ),
            Tool(
                name="search_nasa_info",
                func=search_nasa_info,
                description="Search NASA websites and resources for authoritative astronomy information. Use this for scientific facts and recent discoveries."
            )
        ]
        
        return tools
    
    def generate_questions(self, topic: str) -> List[str]:
        """
        Generate relevant questions about an astronomy topic.
        
        Args:
            topic (str): Astronomy topic to explore
            
        Returns:
            List[str]: List of generated questions
        """
        return self.question_generator.generate_questions(topic)
    
    def search_for_answer(self, question: str) -> str:
        """
        Search for an answer to a specific question using the ReAct agent.
        
        Args:
            question (str): Question to find answer for
            
        Returns:
            str: Retrieved answer
        """
        try:
            # Use the ReAct agent to find the answer
            result = self.agent.run(
                f"Find a comprehensive answer to this astronomy question: {question}. "
                f"Search multiple reliable sources and provide detailed, accurate information."
            )
            return result
        except Exception as e:
            # Fallback to direct web scraping
            print(f"Agent error: {e}. Using fallback method...")
            return self.web_scraper.search_and_scrape(question)
    
    def run_full_investigation(self, topic: str) -> Dict[str, Any]:
        """
        Run a complete investigation of an astronomy topic.
        
        Args:
            topic (str): Astronomy topic to investigate
            
        Returns:
            Dict[str, Any]: Complete investigation results
        """
        # Generate questions
        questions = self.generate_questions(topic)
        
        # Get answers for each question
        qa_pairs = []
        for question in questions:
            answer = self.search_for_answer(question)
            qa_pairs.append({
                'question': question,
                'answer': answer
            })
        
        return {
            'topic': topic,
            'questions': questions,
            'qa_pairs': qa_pairs
        } 