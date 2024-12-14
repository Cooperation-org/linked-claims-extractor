from setuptools import setup, find_packages

setup(
    name="pdf-parser",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'PyMuPDF',
        'transformers',
        'sentence-transformers',
        'Pillow',
        'chromadb',
    ],
)
