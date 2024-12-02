import os
import pytest
import json
from pprint import pprint
from unittest.mock import Mock, patch
from claim_extractor import ClaimExtractor
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

# Sample text inputs and desired outputs
should = (("""Our program helped 100 farmers increase their yield by 25% in 2023,
                 resulting in an additional $50,000 in income per farmer.""",
           """[
         {"amt": 5000000,
          "aspect": "impact:financial",
          "claim": "impact",
          "claimAddress": "",
          "confidence": 1,
          "effectiveDate": "2023-01-01T00:00:00.000Z",
          "howKnown": "FIRST_HAND",
          "images": [],
          "name": "",
          "object": "",
          "sourceURI": "",
          "stars": 0,
          "statement": "Our program helped 100 farmers increase their yield by 25% in 2023, resulting in an additional $50,000 in income per farmer.",
          "subject": "Our program",
          "unit": "usd"}
        ]"""),

    (
       """Review of PillTime (/review/pilltime.co.uk)<img alt="" data-consumer-avatar-image="true" src="https://user-images.trustpilot.com/5f6721cbabba77002a797688/73x73.png" decoding="async" data-nimg="intrinsic" style="position:absolute;top:0;left:0;bottom:0;right:0;box-sizing:border-box;padding:0;border:none;margin:auto;display:block;width:0;height:0;min-width:100%;max-width:100%;min-height:100%;max-height:100%" loading="lazy"/>Darren Wallace21 reviewsGB (/users/5f6721cbabba77002a797688)Updated a day agoVerifiedThis company make me need to take headache pills !!! (/reviews/6730bce48452fd664f6f9f71)Started getting my medication from PillTime and I’m not impressed, the whole point is surely to receive your medication in the simple to use day and dated pouches and yet I keep receiving some pills in the pouch and one pill prescription not pouched so I have to still take the pills out of the packet this I find difficult with my hands and further more isn’t the whole idea not to have to do this?? Also now the reel of pouches turn up just rolled up no box as the first lot did and arrive in a mail bag with the boxes of un pouches pills all squashed up in a bag, absolutely disgusting!! Plus four times I have tried to contact them on the website and they never ever get back to me, wish I hadn’t moved over to PillTime… ALSO i see PillTime only respond to those leaving 5 star reviews!! Still thats not many.Date of experience: 06 November 2024""",
        """
           []
        """
    )
)

# Fixed test data for simple tests
SAMPLE_TEXT = should[0][0]
EXPECTED_CLAIMS = should[0][1]

SAMPLE_WITH_LINK = should[1][0]


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
    pprint(result)
    assert isinstance(result, list)  # Now we expect a list since we're returning parsed JSON
    claims = result[0]  # First item in the array
    assert "effectiveDate" in claims

@pytest.mark.integration
def test_default_integration_is_smart():
    """Test actual Anthropic integration. Requires API key."""
    if 'ANTHROPIC_API_KEY' not in os.environ:
        pytest.skip('ANTHROPIC_API_KEY not found in environment')
    extractor = ClaimExtractor()
    result = extractor.extract_claims(SAMPLE_TEXT)
    assert isinstance(result, list)
    assert result[0]['amt'] == 5000000


@pytest.mark.integration
def test_default_integration_reads_links():
    """Test actual Anthropic integration. Requires API key."""
    if 'ANTHROPIC_API_KEY' not in os.environ:
        pytest.skip('ANTHROPIC_API_KEY not found in environment')
    extractor = ClaimExtractor()
    result = extractor.extract_claims(SAMPLE_WITH_LINK)
    assert isinstance(result, list)
    assert result[0]['subject'] == 'https://www.trustpilot.com/review/pilltime.co.uk'



def test_extract_claims_from_url(extractor):
    """Test URL extraction."""
    url = "https://example.com/article"
    with patch('requests.get') as mock_get:
        mock_get.return_value.text = SAMPLE_TEXT
        mock_get.return_value.raise_for_status = lambda: None
        result = extractor.extract_claims_from_url(url)
        assert isinstance(result, list)
        assert "effectiveDate" in result[0]

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
