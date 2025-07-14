# Linked Claims Extractor - Quick Setup Guide

## What This Does

This project extracts claims from PDFs and text using AI, then lets you publish them to LinkedTrust. It has two main parts:

1. **claim_extractor** - Python library for extracting claims using Claude/OpenAI
2. **pdf_parser** - Web app for uploading PDFs and managing claims

## Quick Start (5 minutes)

### 1. Clone and Setup Environment

```bash
git clone [your-repo-url]
cd linked-claims-extractor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install the web app dependencies
cd pdf_parser
pip install -r requirements.txt
pip install -e .
cd ..

# Install the claim extractor library
cd claim_extractor
pip install -e .
cd ..
```

### 3. Set Environment Variables

Create a `.env` file in the `pdf_parser` directory:

```bash
# Required for claim extraction
ANTHROPIC_API_KEY=your-claude-api-key-here
CLAUDE_MODEL=claude-3-sonnet-20240229
CLAUDE_MAX_TOKENS=4096

# Required for LinkedTrust publishing (optional)
LINKEDTRUST_EMAIL=your-email@example.com
LINKEDTRUST_PASSWORD=your-password
LINKEDTRUST_BASE_URL=https://dev.linkedtrust.us

# Flask settings
FLASK_SECRET_KEY=any-random-string-here
FLASK_PORT=5050
FLASK_DEBUG=True
```

### 4. Run the Web App

```bash
cd pdf_parser
python src/app.py
```

Open http://localhost:5050 in your browser!

## How to Use

1. **Upload a PDF**: Click "Upload File" and select a PDF
2. **View Claims**: The system will extract claims and show them
3. **Publish to LinkedTrust**: Select claims and click "Publish" (requires LinkedTrust credentials)

## Running Tests

```bash
# Test the claim extractor
cd claim_extractor
pytest tests/

# Test the PDF parser (if tests exist)
cd pdf_parser
pytest tests/
```

## Common Issues

**"No module named 'claim_extractor'"**
- Make sure you installed both packages with `pip install -e .`

**"ANTHROPIC_API_KEY not found"**
- Create the `.env` file in the `pdf_parser` directory
- Get an API key from https://console.anthropic.com/

**"Failed to authenticate with LinkedTrust"**
- LinkedTrust credentials are optional for basic use
- You can still extract claims without them

## Project Structure

```
linked-claims-extractor/
├── claim_extractor/       # Core library (published to PyPI)
│   ├── src/              # Source code
│   └── tests/            # Tests
├── pdf_parser/           # Web application
│   ├── src/              # Flask app and PDF processing
│   ├── templates/        # HTML templates
│   └── requirements.txt  # Dependencies
└── service/              # API service (separate deployment)
```

## For Developers

See [DEVELOPMENT.md](DEVELOPMENT.md) for:
- Setting up pre-commit hooks
- Running tests
- Contributing guidelines
- API documentation
