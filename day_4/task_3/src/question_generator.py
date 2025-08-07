"""
Question Generator - LLM-based question generation for astronomy topics
Uses Gemini LLM to generate relevant, investigative questions about astronomy topics.
"""

from typing import List
from langchain.schema import HumanMessage, SystemMessage

class QuestionGenerator:
    """
    Generates relevant astronomy questions using LLM.
    """
    
    def __init__(self, llm):
        """
        Initialize the question generator.
        
        Args:
            llm: LangChain LLM instance (Gemini)
        """
        self.llm = llm
    
    def generate_questions(self, topic: str) -> List[str]:
        """
        Generate 5-6 relevant questions about an astronomy topic.
        
        Args:
            topic (str): Astronomy topic to generate questions for
            
        Returns:
            List[str]: List of generated questions
        """
        system_prompt = """You are an expert astronomy educator. Your task is to generate 5-6 relevant, 
        investigative questions about an astronomy topic that would help someone learn about its features, 
        significance, and discoveries.
        
        Guidelines for question generation:
        1. Questions should be specific and focused on the topic
        2. Include questions about historical discoveries and significance
        3. Ask about current research and recent findings
        4. Include questions about the scientific importance
        5. Questions should be educational and informative
        6. Avoid overly basic or overly complex questions
        7. Focus on what makes this topic interesting and important in astronomy
        
        Generate exactly 5-6 questions that follow this format:
        1. [Question about basic features/definition]
        2. [Question about historical discovery/significance]
        3. [Question about current research/recent findings]
        4. [Question about scientific importance/impact]
        5. [Question about interesting facts or phenomena]
        6. [Question about future research or implications]
        
        Return only the numbered questions, one per line, without any additional text."""
        
        user_prompt = f"Generate 5-6 relevant astronomy questions about: {topic}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            questions = self._parse_questions(response.content)
            return questions[:6]  # Ensure we get exactly 5-6 questions
        except Exception as e:
            print(f"Error generating questions: {e}")
            # Fallback questions
            return self._get_fallback_questions(topic)
    
    def _parse_questions(self, response: str) -> List[str]:
        """
        Parse the LLM response to extract questions.
        
        Args:
            response (str): LLM response containing questions
            
        Returns:
            List[str]: Parsed questions
        """
        lines = response.strip().split('\n')
        questions = []
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('•') or line.startswith('-')):
                # Remove numbering and clean up
                question = line
                if '. ' in question:
                    question = question.split('. ', 1)[1]
                elif ') ' in question:
                    question = question.split(') ', 1)[1]
                elif ' ' in question and question[0] in '123456789':
                    question = question.split(' ', 1)[1]
                
                if question and len(question) > 10:  # Ensure it's a real question
                    questions.append(question)
        
        return questions
    
    def _get_fallback_questions(self, topic: str) -> List[str]:
        """
        Provide fallback questions if LLM generation fails.
        
        Args:
            topic (str): Astronomy topic
            
        Returns:
            List[str]: Fallback questions
        """
        fallback_questions = [
            f"What is {topic} and how is it defined in astronomy?",
            f"What are the key features and characteristics of {topic}?",
            f"How was {topic} discovered and what is its historical significance?",
            f"What recent discoveries or research has been done on {topic}?",
            f"Why is {topic} important for our understanding of the universe?",
            f"What are some interesting or surprising facts about {topic}?"
        ]
        
        return fallback_questions 