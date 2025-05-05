# src/claim_extractor/schemas/loader.py
from pathlib import Path
import requests
from urllib.parse import urlparse

LINKED_CLAIM = 'LINKED_CLAIM'
OPEN_CRED = 'OPEN_CRED'
LINKED_TRUST = 'LINKED_TRUST'

CLAIM_SCHEMAS = {
    LINKED_CLAIM: "http://cooperation.org/credentials/v1/",
    OPEN_CRED: "open_cred.json",
    LINKED_TRUST: "linked_trust.json"
}

CLAIM_METAS = {
    LINKED_TRUST: "linked_trust.meta"
}

def load_schema_info(schema_id: str) -> (str, str):
    """
    Load the schema and meta info for use with the extractor
    """
    schema_str = load_raw_schema(schema_id).replace("{", "{{").replace("}", "}}")

    if schema_id in CLAIM_METAS:
        meta_file = Path(__file__).parent / CLAIM_METAS.get(schema_id)
        with open(meta_file, encoding='utf-8') as f:
            meta_info = f.read()
    else:
       meta_info = ''

    return (schema_str, meta_info)


def load_raw_schema(schema_id: str) -> str:
    """
    Load schema content from either URL or local file.
    
    Args:
        schema_id: Either a known schema ID from CLAIM_SCHEMAS or a path/URL
        
    Returns:
        str: Raw schema content
    """
    # Get location from known schemas if applicable
    schema_location = CLAIM_SCHEMAS.get(schema_id, schema_id)
    
    # Check if it's a URL
    parsed = urlparse(schema_location)
    if parsed.scheme and parsed.netloc:
        response = requests.get(schema_location)
        response.raise_for_status()
        return response.text
        
    # Otherwise load local file
    schema_path = Path(__file__).parent / schema_location
    with open(schema_path, encoding='utf-8') as f:
        return f.read()
