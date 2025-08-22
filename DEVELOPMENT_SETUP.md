# Local Development Setup

## Quick Setup
1. Create virtual environment: `python -m venv venv`
2. Activate: `venv\Scripts\activate` (Windows)
3. Install core dependencies: `pip install langchain langchain-anthropic python-dotenv requests`
4. Configure `.env` file with API keys
5. Test with: `python test_extractor.py`

## Required Environment Variables
ANTHROPIC_API_KEY=your_api_key_here
CLAUDE_MODEL=claude-3-5-sonnet-20241022
CLAUDE_MAX_TOKENS=4096

## Common Issues
- Use minimal dependencies to avoid spacy/thinc conflicts
- Activate virtual environment before running scripts
- Update model names if you get 404 errors