import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from claim_extractor import ClaimExtractor


class TestClaimExtractor(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_llm = Mock()
        self.extractor = ClaimExtractor(llm=self.mock_llm)
        
    def test_extract_claims_success(self):
        """Test successful claim extraction"""
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = json.dumps([
            {
                "subject": "https://example.com/entity/John_Smith",
                "claim": "performed",
                "object": "https://example.com/entity/TechCorp",
                "howKnown": "DOCUMENT",
                "confidence": 0.95
            }
        ])
        self.mock_llm.invoke.return_value = mock_response
        
        # Test extraction
        text = "John Smith was the CEO of TechCorp from 2020 to 2023."
        claims = self.extractor.extract_claims(text)
        
        # Verify
        self.assertEqual(len(claims), 1)
        self.assertEqual(claims[0]["subject"], "https://example.com/entity/John_Smith")
        self.assertEqual(claims[0]["claim"], "performed")
        self.mock_llm.invoke.assert_called_once()
        
    def test_extract_claims_empty_response(self):
        """Test handling of empty response"""
        mock_response = Mock()
        mock_response.content = json.dumps([])
        self.mock_llm.invoke.return_value = mock_response
        
        claims = self.extractor.extract_claims("No claims here.")
        
        self.assertEqual(claims, [])
        
    def test_extract_claims_invalid_json(self):
        """Test handling of invalid JSON response"""
        mock_response = Mock()
        mock_response.content = "This is not JSON"
        self.mock_llm.invoke.return_value = mock_response
        
        claims = self.extractor.extract_claims("Some text")
        
        self.assertEqual(claims, [])
        
    def test_extract_claims_llm_error(self):
        """Test handling of LLM errors"""
        self.mock_llm.invoke.side_effect = Exception("API Error")
        
        claims = self.extractor.extract_claims("Some text")
        
        self.assertEqual(claims, [])
        
    def test_extract_claims_with_multiple_claims(self):
        """Test extraction of multiple claims"""
        mock_response = Mock()
        mock_response.content = json.dumps([
            {
                "subject": "https://example.com/entity/Company_A",
                "claim": "owns",
                "object": "https://example.com/entity/Company_B",
                "confidence": 0.9
            },
            {
                "subject": "https://example.com/entity/Company_A", 
                "claim": "funds_for_purpose",
                "object": "https://example.com/transaction/acquisition_1B",
                "amt": 1000000000,
                "unit": "USD",
                "confidence": 0.85
            }
        ])
        self.mock_llm.invoke.return_value = mock_response
        
        text = "Company A acquired Company B for $1 billion."
        claims = self.extractor.extract_claims(text)
        
        self.assertEqual(len(claims), 2)
        self.assertEqual(claims[0]["object"], "https://example.com/entity/Company_B")
        self.assertEqual(claims[1]["amt"], 1000000000)
        
    @patch('claim_extractor.llm_extract.requests')
    def test_extract_claims_from_url(self, mock_requests):
        """Test URL extraction"""
        # Mock URL response
        mock_requests.get.return_value.text = "Test content from URL"
        mock_requests.get.return_value.raise_for_status = Mock()
        
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = json.dumps([
            {"subject": "https://example.com/test", "claim": "validated", "object": "https://example.com/url"}
        ])
        self.mock_llm.invoke.return_value = mock_response
        
        claims = self.extractor.extract_claims_from_url("https://example.com")
        
        self.assertEqual(len(claims), 1)
        mock_requests.get.assert_called_once_with("https://example.com")


if __name__ == '__main__':
    unittest.main()