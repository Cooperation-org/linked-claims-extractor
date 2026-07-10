# src/claim_extractor/__init__.py
from importlib.metadata import version, PackageNotFoundError

from .llm_extract import ClaimExtractor

try:
    __version__ = version("linked-claims-extractor")
except PackageNotFoundError:
    __version__ = "0.1.1"

__all__ = [
    "ClaimExtractor",
]
