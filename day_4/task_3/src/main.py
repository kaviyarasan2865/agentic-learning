#!/usr/bin/env python3
"""
Astronomy Fact Finder - Main Application
Uses ReAct pattern with LangChain and Gemini LLM to generate astronomy fact sheets.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src directory to path
sys.path.append(str(Path(__file__).parent))

from agent import AstronomyAgent
from fact_sheet_generator import FactSheetGenerator

def load_environment():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    else:
        print("Warning: .env file not found. Please create one with your GEMINI_API_KEY.")
        print("You can copy env_example.txt to .env and add your API key.")

def run_astronomy_fact_finder(topic=None):
    """
    Run the Astronomy Fact Finder for a given topic.
    
    Args:
        topic (str): Astronomy topic to explore. If None, will prompt user.
    """
    print("🌌 Astronomy Fact Finder 🌌")
    print("=" * 50)
    
    # Load environment
    load_environment()
    
    # Get API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in environment variables.")
        print("Please set your Gemini API key in the .env file.")
        return
    
    # Get topic from user if not provided
    if not topic:
        print("\nEnter an astronomy topic to explore:")
        print("Examples: black holes, exoplanets, supernovae, dark matter, etc.")
        topic = input("Topic: ").strip()
        
        if not topic:
            print("❌ No topic provided. Exiting.")
            return
    
    print(f"\n🔍 Exploring: {topic}")
    print("=" * 50)
    
    try:
        # Initialize the agent
        agent = AstronomyAgent(api_key)
        
        # Generate questions
        print("\n🤔 Generating questions...")
        questions = agent.generate_questions(topic)
        
        print(f"✅ Generated {len(questions)} questions:")
        for i, question in enumerate(questions, 1):
            print(f"  {i}. {question}")
        
        # Get answers for each question
        print("\n🔍 Searching for answers...")
        qa_pairs = []
        
        for i, question in enumerate(questions, 1):
            print(f"\n  Question {i}/{len(questions)}: {question}")
            answer = agent.search_for_answer(question)
            qa_pairs.append((question, answer))
            print(f"  ✅ Answer found")
        
        # Generate fact sheet
        print("\n📝 Generating fact sheet...")
        fact_sheet_gen = FactSheetGenerator()
        fact_sheet = fact_sheet_gen.generate_fact_sheet(topic, qa_pairs)
        
        # Save fact sheet
        output_dir = Path(__file__).parent.parent / 'output'
        output_dir.mkdir(exist_ok=True)
        
        filename = f"{topic.replace(' ', '_').lower()}_fact_sheet.md"
        output_path = output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(fact_sheet)
        
        print(f"\n✅ Fact sheet saved to: {output_path}")
        print("\n🎉 Astronomy Fact Finder completed successfully!")
        
        # Display preview
        print("\n📄 Fact Sheet Preview:")
        print("=" * 50)
        print(fact_sheet[:1000] + "..." if len(fact_sheet) > 1000 else fact_sheet)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Please check your API key and internet connection.")

def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        topic = ' '.join(sys.argv[1:])
        run_astronomy_fact_finder(topic)
    else:
        run_astronomy_fact_finder()

if __name__ == "__main__":
    main() 