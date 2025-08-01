# Linked Claims Extractor

Extract structured claims from text, URLs, and PDFs using AI-powered language models (LLMs).

## Installation

```bash
pip install linked-claims-extractor
```

## About

This is the core Python library for extracting structured claims from unstructured text. It supports:

- Text extraction from multiple sources (raw text, URLs, PDFs)
- Multiple AI providers (Anthropic Claude, OpenAI GPT)
- Customizable schemas for different claim types
- Easy integration into Python applications

## Related Projects

- **[linked-claims-extraction-service](https://github.com/Cooperation-org/linked-claims-extraction-service)**: Web service and API for PDF processing and claim extraction (deployed at https://extract.linkedtrust.us)
- **[linked-claims-research](https://github.com/Cooperation-org/linked-claims-research)**: Research playground for experimental claim extraction approaches

## Quick Start

```python
from claim_extractor import ClaimExtractor

# Initialize extractor
extractor = ClaimExtractor()

# Extract claims from text
claims = extractor.extract_claims("Your text here...")

# Extract from URL
claims = extractor.extract_from_url("https://example.com/article")

# Extract from PDF
claims = extractor.extract_from_pdf("path/to/document.pdf")
```

## Documentation

See the [claim_extractor/README.md](./claim_extractor/README.md) for detailed documentation.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
