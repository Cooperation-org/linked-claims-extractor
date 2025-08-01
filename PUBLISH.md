# Publish updates to Pypi manually

```
rm -rf dist/ build/
python -m build
python -m twine upload dist/*
```
