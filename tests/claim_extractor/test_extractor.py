# tests/test_extractor.py
import json
import os
import pytest
from unittest.mock import Mock, patch
from claim_extractor import ClaimExtractor
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

# Sample test data
SAMPLE_TEXT = """Our program helped 100 farmers increase their yield by 25% in 2023,
                 resulting in an additional $50,000 in income per farmer."""

EXPECTED_CLAIMS = """[
    {
        "type": "LinkedClaim",
        "claim": "Program increased farmer yields",
        "aspect": "agricultural_productivity",
        "statement": "100 farmers increased yield by 25%",
        "object": "farmers",
        "source": {
            "type": "ClaimSource",
            "dateObserved": "2023"
        }
    }
]"""


@pytest.fixture
def mock_llm():
    mock = Mock()
    mock.return_value.content = EXPECTED_CLAIMS
    return mock

@pytest.fixture
def extractor(mock_llm):
    return ClaimExtractor(llm=mock_llm)

def test_extract_claims(extractor):
    """Test basic claim extraction."""
    result = extractor.extract_claims(SAMPLE_TEXT)
    assert isinstance(result, str)
    assert "LinkedClaim" in result

@pytest.mark.integration
def test_openai_integration():
    """Test actual OpenAI integration. Requires API key."""
    if 'OPENAI_API_KEY' not in os.environ:
        pytest.skip('OPENAI_API_KEY not found in environment')
        
    llm = ChatOpenAI(temperature=0)
    extractor = ClaimExtractor(llm=llm)
    result = extractor.extract_claims(SAMPLE_TEXT)
    import pdb; pdb.set_trace()
    assert isinstance(result, str)
    assert "LinkedClaim" in result

@pytest.mark.vcr  # If using VCR.py for request recording
def test_extract_claims_from_url(extractor):
    """Test URL extraction."""
    url = "https://example.com/article"
    with patch('requests.get') as mock_get:
        mock_get.return_value.text = SAMPLE_TEXT
        mock_get.return_value.raise_for_status = lambda: None
        
        result = extractor.extract_claims_from_url(url)
        assert isinstance(result, str)
        assert "LinkedClaim" in result

def test_schema_loading(extractor):
    """Test schema was loaded properly."""
    assert extractor.schema is not None
    unescaped_schema = extractor.schema.replace("{{", "{").replace("}}", "}")
    
    # Parse as JSON
    schema_json = json.loads(unescaped_schema)
    
    # Check for expected fields
    assert "subject" in schema_json

def test_invalid_url():
    """Test handling of invalid URLs."""
    extractor = ClaimExtractor()
    with pytest.raises(Exception):  # or more specific exception
        extractor.extract_claims_from_url("not-a-real-url")
