"""
LinkedTrust API Client for publishing signed claims.

This module handles the communication with the LinkedTrust API service,
including authentication, claim formatting, and submission.
"""

import json
import time
import requests
import logging
from typing import Dict, List, Any, Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LinkedTrustClient:
    """Client for interacting with the LinkedTrust API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: str = "https://live.linkedtrust.us/api",
        private_key_path: Optional[str] = None,
    ):
        """
        Initialize the LinkedTrust API client.

        Args:
            api_key: API key for authentication (if None, loads from env var)
            api_url: Base URL for the LinkedTrust API
            private_key_path: Path to the private key file for signing claims
        """
        self.api_key = api_key or os.getenv("LINKEDTRUST_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required, either pass directly or set LINKEDTRUST_API_KEY env var")
        
        self.api_url = api_url
        
        # Load private key for signing
        self.private_key = None
        if private_key_path:
            self._load_private_key(private_key_path)
        elif os.getenv("LINKEDTRUST_PRIVATE_KEY_PATH"):
            self._load_private_key(os.getenv("LINKEDTRUST_PRIVATE_KEY_PATH"))
        else:
            logger.warning("No private key provided, claims will not be signed")
    
    def _load_private_key(self, key_path: str) -> None:
        """
        Load a private key from a PEM file.
        
        Args:
            key_path: Path to the PEM-encoded private key file
        """
        try:
            with open(key_path, "rb") as key_file:
                key_data = key_file.read()
                # You might need a password if the key is encrypted
                password = os.getenv("LINKEDTRUST_KEY_PASSWORD")
                self.private_key = load_pem_private_key(
                    key_data,
                    password=password.encode() if password else None
                )
            logger.info(f"Successfully loaded private key from {key_path}")
        except Exception as e:
            logger.error(f"Failed to load private key: {str(e)}")
            raise
    
    def sign_claim(self, claim: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sign a claim with the private key.
        
        Args:
            claim: The claim data to sign
            
        Returns:
            The claim with signature field added
        """
        if not self.private_key:
            logger.warning("No private key available, returning unsigned claim")
            return claim
        
        # Create a deterministic representation of the claim for signing
        # Remove any existing signature field
        claim_copy = claim.copy()
        claim_copy.pop("signature", None)
        
        # Sort keys for deterministic serialization
        message = json.dumps(claim_copy, sort_keys=True).encode()
        
        # Sign the message
        if isinstance(self.private_key, rsa.RSAPrivateKey):
            signature = self.private_key.sign(
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            # Add signature to claim
            claim_copy["signature"] = signature.hex()
            return claim_copy
        else:
            logger.error("Unsupported private key type")
            return claim
    
    def format_claim(self, claim: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a claim to match the LinkedTrust API requirements.
        
        Args:
            claim: Raw claim data from the extractor
            
        Returns:
            Formatted claim ready for submission
        """
        # Add required fields if missing
        formatted_claim = claim.copy()
        
        # Set defaults for required fields if not present
        if "effectiveDate" not in formatted_claim:
            formatted_claim["effectiveDate"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        
        if "howKnown" not in formatted_claim:
            formatted_claim["howKnown"] = "WEB_DOCUMENT"
        
        if "confidence" not in formatted_claim:
            # Default confidence score based on presence of statement field
            formatted_claim["confidence"] = 0.9 if "statement" in formatted_claim else 0.7
        
        # Ensure structure is compliant with API expectations
        return formatted_claim
    
    def validate_claim(self, claim: Dict[str, Any]) -> bool:
        """
        Validate that a claim has all required fields for the LinkedTrust API.
        
        Args:
            claim: The claim to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["subject", "claim", "statement"]
        
        # Check for required fields
        for field in required_fields:
            if field not in claim or not claim[field]:
                logger.error(f"Claim is missing required field: {field}")
                return False
        
        # Validate claim type
        valid_claim_types = ["impact", "rated", "same_as"]
        if claim["claim"] not in valid_claim_types:
            logger.error(f"Invalid claim type: {claim['claim']}")
            return False
        
        return True
    
    def submit_claim(self, claim: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit a claim to the LinkedTrust API.
        
        Args:
            claim: The claim to submit
            
        Returns:
            API response data
        """
        # Validate the claim
        if not self.validate_claim(claim):
            raise ValueError("Invalid claim format")
        
        # Format the claim
        formatted_claim = self.format_claim(claim)
        
        # Sign the claim if private key is available
        if self.private_key:
            signed_claim = self.sign_claim(formatted_claim)
        else:
            signed_claim = formatted_claim
        
        # Prepare the request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Submit to API
        try:
            response = requests.post(
                f"{self.api_url}/v1/claims",
                headers=headers,
                json=signed_claim
            )
            
            # Check for success
            response.raise_for_status()
            
            # Return response data
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to submit claim: {str(e)}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise
    
    def submit_claims_batch(self, claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Submit multiple claims to the LinkedTrust API.
        
        Args:
            claims: List of claims to submit
            
        Returns:
            List of API responses
        """
        results = []
        
        for i, claim in enumerate(claims):
            try:
                logger.info(f"Submitting claim {i+1}/{len(claims)}")
                result = self.submit_claim(claim)
                results.append({"success": True, "result": result, "claim": claim})
            except Exception as e:
                logger.error(f"Error submitting claim {i+1}: {str(e)}")
                results.append({"success": False, "error": str(e), "claim": claim})
        
        return results


# Example usage
if __name__ == "__main__":
    client = LinkedTrustClient()
    
    # Example claim
    test_claim = {
        "subject": "Gates Foundation",
        "claim": "impact",
        "statement": "The Gates Foundation helped vaccinate over 10 million children in 2019.",
        "aspect": "impact:social",
        "amt": 10000000,
        "unit": "children"
    }
    
    # Submit single claim
    response = client.submit_claim(test_claim)
    print(f"Response: {response}")
