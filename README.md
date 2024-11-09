# linked-claims-extractor
Extract claims from text, url or pdf using AI LLMs to help

## Installation and Usage

`pip install linked-claims-extractor`

Default is to use Anthropic which requires setting
`export ANTHROPIC_API_KEY=...`

```
from claim_extractor import ClaimExtractor

extractor = ClaimExtractor()
# or extractor = ClaimExtractor(llm=your_llm, schema=schema_from_list)

result = extractor.extract_claims('some text')

pprint(json.loads(result))
```

## Developer Environment

This project uses pyproject.toml for dependencies

```
python -m venv .venv
. .venv/bin/activate
pip install -e .
```

## Testing and Debugging

```
pytest -s --pdb
```
