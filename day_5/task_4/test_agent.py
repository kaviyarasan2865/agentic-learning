#!/usr/bin/env python3
"""
Test script for Event Report Analyzer Agent
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agent import EventReportAnalyzerAgent

def test_agent():
    print("🧪 Testing Event Report Analyzer Agent")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in .env file")
        return
    
    print("✅ API key found")
    
    # Check PDF exists
    pdf_path = "data/event_report.pdf"
    if not Path(pdf_path).exists():
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    print(f"✅ PDF found: {pdf_path}")
    
    try:
        # Initialize agent
        print("🔧 Initializing agent...")
        agent = EventReportAnalyzerAgent()
        
        # Process PDF
        print("📄 Processing PDF...")
        success = agent.process_pdf(pdf_path)
        
        if not success:
            print("❌ Failed to process PDF")
            return
        
        print(f"✅ PDF processed: {len(agent.documents)} documents")
        print(f"✅ Agent initialized: {agent.agent is not None}")
        print(f"✅ Tools available: {len(agent.tools)}")
        
        # Test a simple question
        print("\n🧪 Testing question: 'What is this event about?'")
        response = agent.run_agent("What is this event about?")
        
        print("\n🤖 Agent Response:")
        print("-" * 50)
        print(response)
        print("-" * 50)
        
        if "No documents loaded" in response or "Error" in response:
            print("❌ Agent is not working properly")
        else:
            print("✅ Agent is working correctly!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_agent()
