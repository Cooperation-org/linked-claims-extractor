\# Local Development Setup Issues and Solutions



\## Problems Encountered During Initial Setup



1\. \*\*Dependency Conflicts\*\*: The `req.txt` files contain conflicting package versions, particularly between `spacy` and `thinc`

2\. \*\*Missing SSH Keys\*\*: PDF parser component tries to clone private repositories via SSH

3\. \*\*Complex Project Structure\*\*: Two separate projects with different setup requirements

4\. \*\*Unclear Installation Instructions\*\*: No clear minimal setup path for development



\## Solutions



\### Minimal Working Setup

1\. Create virtual environment: `python -m venv venv`

2\. Activate: `venv\\Scripts\\activate` (Windows)

3\. Install core dependencies: `pip install langchain langchain-anthropic python-dotenv requests`

4\. Configure `.env` file with API keys

5\. Use the provided `test\_extractor.py` script



\### Required Environment Variables
ANTHROPIC\_API\_KEY=your\_api\_key\_here

CLAUDE\_MODEL=claude-3-sonnet-20240229

CLAUDE\_MAX\_TOKENS=4096

