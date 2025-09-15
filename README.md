# Claim Extractor

Extract [LinkedClaims](https://identity.foundation/labs-linkedclaims/) from text using LLMs.

## Quick Start

```python
from claim_extractor import ClaimExtractor

# Initialize
extractor = ClaimExtractor()

## OPTIONALLY include extra instructions and override default message prompt

extractor=ClaimExtractor(extra_system_instructions="Only look for claims about islands", message_prompt="The following narrative may or may not have claims in it, include any claims about islands and especially trees on islands. Otherwise return empty array if not found.  Here is the text {text}")

# Extract claims from text
text = "John Smith was the CEO of TechCorp from 2020 to 2023 and increased revenue by 40%."
claims = extractor.extract_claims(text)

# Returns:
# [
#   {
#     "subject": "urn:person:John_Smith",
#     "claim": "controlled", 
#     "object": "urn:company:TechCorp",
      "effectiveDate": 2020,
      "statement": "John Smith was the CEO of TechCorp from 2020 to 2023",
#     "howKnown": "DOCUMENT",
#   },
#   {
#     "subject": "urn:person:John_Smith",
#     "claim": "impact:revenue",
#     "object": "urn:company:TechCorp",
#     "amt": 1.4,
#     "effectiveDate": 2023,
#     "statement": "John Smith increased revenue of Tech Corp by 40% from 2020 to 2023"
#   }
# ]
```

## Installation

### From PyPI

```bash
pip install linked-claims-extractor
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/Cooperation-org/linked-claims-extractor.git
cd linked-claims-extractor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install build tools (optional, for publishing)
pip install build twine
```

For publishing instructions, see [PUBLISH.md](PUBLISH.md).

### Configuration

Set environment variable:
```bash
export ANTHROPIC_API_KEY=your-key
```

Or create a `.env` file:
```bash
ANTHROPIC_API_KEY=your-key
```

## Usage

```python
from claim_extractor import ClaimExtractor

# Basic usage
extractor = ClaimExtractor()
claims = extractor.extract_claims("Your text here...")

# Extract from URL
claims = extractor.extract_claims_from_url("https://example.com/article")
```

## Related Projects

- **[linked-claims-extraction-service](https://github.com/Cooperation-org/linked-claims-extraction-service)**: Web service for publishing claims to LinkedTrust
