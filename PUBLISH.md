# Publishing to PyPI

## Prerequisites
- Virtual environment activated with dev setup from README.md
- `build` and `twine` installed: `pip install build twine`

## Publish Steps

1. Update version in `pyproject.toml`

2. Clean and build:
```bash
rm -rf dist/ build/
python -m build
```

3. Upload to PyPI:
```bash
python -m twine upload dist/*
```
