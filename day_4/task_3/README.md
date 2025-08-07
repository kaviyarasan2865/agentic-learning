# Astronomy Fact Finder

An intelligent agent that explores astronomy topics using the ReAct pattern to generate questions, retrieve answers from free astronomy websites, and compile comprehensive fact sheets.

## Features

- **ReAct Pattern Implementation**: Uses LangChain's initialize_agent with reasoning and action capabilities
- **Gemini LLM Integration**: Leverages Google's Gemini model for question generation and reasoning
- **Web Scraping**: Retrieves accurate information from free astronomy resources
- **Fact Sheet Generation**: Produces structured markdown reports with questions and answers
- **Educational Focus**: Designed to educate about celestial phenomena

## Project Structure

```
task_3/
├── src/
│   ├── main.py              # Main application entry point
│   ├── agent.py             # ReAct agent implementation
│   ├── question_generator.py # LLM-based question generation
│   ├── web_scraper.py       # Web scraping utilities
│   └── fact_sheet_generator.py # Markdown fact sheet creation
├── output/                  # Generated fact sheets
├── docs/                    # Documentation
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore file
└── README.md               # This file
```

## Setup

### Prerequisites

- Python 3.8 or higher
- Google Cloud account with Gemini API access

### Installation

1. **Clone the repository** (if applicable)

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Usage

### Running the Astronomy Fact Finder

1. **Activate your virtual environment** (if not already active)

2. **Run the main application**:
   ```bash
   python src/main.py
   ```

3. **Follow the prompts** to specify an astronomy topic

4. **View the generated fact sheet** in the `output/` directory

### Example Usage

```python
from src.main import run_astronomy_fact_finder

# Run with a specific topic
run_astronomy_fact_finder("black holes")
```

## Dependencies

- **langchain**: Framework for building LLM applications
- **langchain-google-genai**: Google Gemini integration for LangChain
- **google-generativeai**: Official Google Generative AI SDK
- **requests**: HTTP library for web requests
- **beautifulsoup4**: HTML parsing for web scraping
- **markdown**: Markdown processing
- **python-dotenv**: Environment variable management
- **lxml**: XML/HTML processing

## Output

The application generates structured markdown fact sheets containing:
- Topic overview
- Generated questions (5-6 per topic)
- Detailed answers from reliable sources
- Educational insights about celestial phenomena

## ReAct Pattern Implementation

The agent follows the ReAct (Reasoning + Acting) pattern:

1. **Reasoning**: LLM generates relevant astronomy questions
2. **Acting**: Web scraping retrieves answers from free astronomy resources
3. **Reflection**: Agent compiles findings into comprehensive fact sheets

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is for educational purposes as part of the agentic learning curriculum. 