# Linked Claims Extractor

The **Linked Claims Extractor** is a tool that uses AI language models to extract claims from text, URLs, or PDFs. It supports multiple LLMs, including Anthropic and OpenAI, and allows users to define custom schemas for claim extraction.

---

## Installation

To install the Linked Claims Extractor, run:

```bash
pip install linked-claims-extractor
```

You will need to set the `ANTHROPIC_API_KEY` environment variable if you are using the Anthropic model:

```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

---

## Usage

### Extracting Claims from Text
```python
from claim_extractor import ClaimExtractor

extractor = ClaimExtractor()
result = extractor.extract_claims('some text')

import pprint
pprint.pprint(result)
```

### Extracting Claims from a URL
```python
result = extractor.extract_claims_from_url('https://example.com')
pprint.pprint(result)
```

---

## Development and Testing

To set up the development environment, run:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

To run tests, use:

```bash
pytest -s --pdb
```

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request with your changes.

---

## License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for more details.
