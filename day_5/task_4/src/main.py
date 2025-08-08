"""
Main Entry Point for Event Report Analyzer

Provides command-line interface for the Event Report Analyzer agent.
"""

import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import EventReportAnalyzerAgent


def create_sample_event_report():
    """Create a sample event report for testing."""
    sample_content = """# Tech Conference 2024 - Event Report

## Event Overview
The Tech Conference 2024 was held on March 15-17, 2024, at the Convention Center in San Francisco. 
The event brought together over 500 technology professionals, industry leaders, and innovators from 
around the world to discuss the latest trends in artificial intelligence, machine learning, and 
emerging technologies.

## Key Outcomes

### Attendance and Engagement
- Total attendees: 523 (exceeding target of 450)
- 85% attendance rate across all sessions
- 92% satisfaction rate based on post-event surveys
- 78% of attendees reported high engagement levels

### Technical Achievements
- 15 keynote presentations delivered
- 45 breakout sessions completed
- 12 hands-on workshops conducted
- 5 panel discussions with industry experts

### Networking and Collaboration
- 200+ business meetings scheduled through the event app
- 15 new partnerships announced
- 50+ startup pitches presented
- 25 mentorship sessions conducted

## Attendee Feedback

### Positive Feedback
- "Excellent keynote speakers and relevant topics"
- "Great networking opportunities and well-organized sessions"
- "High-quality content and knowledgeable presenters"
- "Good balance of technical and business sessions"

### Areas for Improvement
- "Some sessions were too crowded"
- "Need more interactive workshops"
- "Better food options for dietary restrictions"
- "Longer breaks between sessions"

### Satisfaction Metrics
- Overall satisfaction: 4.2/5.0
- Content quality: 4.4/5.0
- Networking opportunities: 4.1/5.0
- Venue and logistics: 3.9/5.0

## Financial Performance
- Revenue: $125,000 (105% of target)
- Sponsorship revenue: $45,000
- Registration revenue: $80,000
- Expenses: $95,000
- Net profit: $30,000

## Strategic Impact
- Established the conference as a premier tech event
- Created platform for industry collaboration
- Generated significant media coverage
- Strengthened community relationships

## Recommendations for Future Events
1. Increase workshop capacity
2. Improve catering options
3. Add more interactive sessions
4. Extend networking time
5. Implement better session scheduling
"""
    
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    sample_file = data_dir / "sample_event_report.txt"
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(sample_content)
    
    print(f"Created sample event report: {sample_file}")
    print("Note: This is a text file. For full functionality, please provide a PDF event report.")


def main():
    """Main entry point for the Event Report Analyzer."""
    parser = argparse.ArgumentParser(
        description="Event Report Analyzer - AI-powered event report analysis using Gemini 2.0 Flash"
    )
    
    parser.add_argument("--pdf", type=str, help="Path to the PDF event report file")
    parser.add_argument("--query", type=str, help="Specific query to answer")
    parser.add_argument("--output", type=str, help="Output file path for comprehensive report")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--create-sample", action="store_true", help="Create a sample event report")
    parser.add_argument("--model", type=str, default="gemini-2.0-flash", 
                       help="Google Gemini model to use (default: gemini-2.0-flash)")
    parser.add_argument("--temperature", type=float, default=0.1, 
                       help="Temperature for model responses (default: 0.1)")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Check for Google API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("Warning: GOOGLE_API_KEY not found in environment variables.")
        print("Please set your Google API key in a .env file or environment variable.")
        print("You can get one from: https://makersuite.google.com/app/apikey")
        return
    
    if args.create_sample:
        create_sample_event_report()
        return
    
    # Initialize agent
    try:
        agent = EventReportAnalyzerAgent(
            model_name=args.model,
            temperature=args.temperature
        )
        print(f"Event Report Analyzer initialized with model: {args.model}")
        
    except Exception as e:
        print(f"Error initializing agent: {str(e)}")
        return
    
    # Process PDF if provided
    if args.pdf:
        if not os.path.exists(args.pdf):
            print(f"Error: PDF file not found: {args.pdf}")
            return
        
        success = agent.process_pdf(args.pdf)
        if not success:
            print("Failed to process PDF. Please check the file and try again.")
            return
        
        print("PDF processed successfully!")
    
    # Handle different modes
    if args.interactive:
        if not args.pdf:
            print("Error: PDF file required for interactive mode. Use --pdf <file>")
            return
        agent.interactive_mode()
        
    elif args.query:
        if not args.pdf:
            print("Error: PDF file required for query mode. Use --pdf <file>")
            return
        response = agent.run_agent(args.query)
        print(f"\nQuery: {args.query}")
        print(f"Response: {response}")
        
    elif args.output:
        if not args.pdf:
            print("Error: PDF file required for report generation. Use --pdf <file>")
            return
        report = agent.generate_comprehensive_report(args.output)
        print("Comprehensive report generated successfully!")
        
    else:
        if args.pdf:
            print("PDF processed successfully!")
            print("Use --query to ask questions, --interactive for interactive mode, or --output to generate a report.")
        else:
            print("Event Report Analyzer - Usage:")
            print("  --pdf <file>     : Process a PDF event report")
            print("  --query <text>   : Ask a specific question about the event")
            print("  --output <file>  : Generate comprehensive report")
            print("  --interactive    : Run in interactive mode")
            print("  --create-sample  : Create a sample event report")
            print("\nExample:")
            print("  python src/main.py --pdf data/event_report.pdf --query 'What were the key outcomes?'")


if __name__ == "__main__":
    main()
