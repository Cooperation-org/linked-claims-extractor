# Claim Extractor

Extract [LinkedClaims](https://identity.foundation/labs-linkedclaims/) from text using LLMs.

## Quick Start

```python
from claim_extractor import ClaimExtractor

# Initialize
extractor = ClaimExtractor()

# Extract claims from text
text = "John Smith was the CEO of TechCorp from 2020 to 2023 and increased revenue by 40%."
claims = extractor.extract_claims(text)

# Returns:
# [
#   {
#     "subject": "https://example.com/entity/John_Smith",
#     "claim": "performed", 
#     "object": "https://example.com/entity/TechCorp",
#     "howKnown": "DOCUMENT",
#     "confidence": 0.95
#   },
#   {
#     "subject": "https://example.com/entity/John_Smith",
#     "claim": "impact",
#     "object": "https://example.com/metric/revenue_increase_40%",
#     "confidence": 0.9
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