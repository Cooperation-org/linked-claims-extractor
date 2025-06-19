#!/usr/bin/env python3
"""
Test script for linked-claims-extractor backend integration
"""

import requests
import json
import time
from datetime import datetime

# Configuration
EXTRACTOR_URL = "http://localhost:5000"
BACKEND_URL = "http://localhost:3000"

# Test credentials (update these)
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword"

def get_auth_token():
    """Get JWT token from backend"""
    print("1. Authenticating with backend...")
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    
    if response.status_code != 200:
        print(f"   ❌ Authentication failed: {response.text}")
        return None
    
    token = response.json().get('accessToken')
    print(f"   ✅ Got auth token")
    return token

def test_extraction_with_approval(token):
    """Test the extraction and approval flow"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 1: Extract claims
    print("\n2. Extracting claims from text...")
    extract_response = requests.post(
        f"{EXTRACTOR_URL}/extract-with-approval",
        headers=headers,
        json={
            "text": """I worked as a Senior Python Developer at TechCorp for 5 years. 
                      During this time, I led a team of 8 developers, implemented 
                      microservices architecture, and improved system performance by 40%.
                      I also mentored junior developers and conducted code reviews.""",
            "schema_name": "SIMPLE_SKILL"
        }
    )
    
    if extract_response.status_code != 200:
        print(f"   ❌ Extraction failed: {extract_response.text}")
        return
    
    extraction_data = extract_response.json()
    approval_id = extraction_data['approval_id']
    claims = extraction_data['claims']
    
    print(f"   ✅ Extracted {len(claims)} claims")
    print(f"   Approval ID: {approval_id}")
    
    # Step 2: Review claims
    print("\n3. Reviewing pending claims...")
    review_response = requests.get(
        f"{EXTRACTOR_URL}/pending-claims/{approval_id}",
        headers=headers
    )
    
    if review_response.status_code != 200:
        print(f"   ❌ Review failed: {review_response.text}")
        return
    
    pending_data = review_response.json()
    print(f"   ✅ Retrieved {len(pending_data['claims'])} pending claims")
    
    # Print claims for review
    print("\n   Extracted claims:")
    for i, claim in enumerate(pending_data['claims']):
        print(f"   [{i}] {claim.get('subject', 'N/A')} - {claim.get('claim', 'N/A')} - {claim.get('object', 'N/A')}")
    
    # Step 3: Approve some claims (approve first 3)
    print("\n4. Approving claims...")
    approve_indices = list(range(min(3, len(claims))))
    
    approve_response = requests.post(
        f"{EXTRACTOR_URL}/approve-claims",
        headers=headers,
        json={
            "approval_id": approval_id,
            "approved_indices": approve_indices
        }
    )
    
    if approve_response.status_code != 200:
        print(f"   ❌ Approval failed: {approve_response.text}")
        return
    
    results = approve_response.json()
    print(f"   ✅ Successfully submitted {len(results['results']['successful'])} claims")
    if results['results']['failed']:
        print(f"   ⚠️  Failed to submit {len(results['results']['failed'])} claims")

def test_direct_submission(token):
    """Test direct claim submission"""
    print("\n5. Testing direct claim submission...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{EXTRACTOR_URL}/submit-claims-direct",
        headers=headers,
        json={
            "claims": [
                {
                    "subject": f"https://linkedtrust.us/test/{int(time.time())}",
                    "claim": "test_claim",
                    "object": "Integration Test",
                    "confidence": 1.0,
                    "howKnown": "DERIVED",
                    "statement": "This is a test claim from the integration script"
                }
            ]
        }
    )
    
    if response.status_code != 200:
        print(f"   ❌ Direct submission failed: {response.text}")
        return
    
    print(f"   ✅ Successfully submitted test claim")

def main():
    print("=== Linked Claims Extractor Integration Test ===")
    print(f"Extractor URL: {EXTRACTOR_URL}")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test started at: {datetime.now()}")
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        return
    
    # Test extraction with approval
    test_extraction_with_approval(token)
    
    # Test direct submission
    test_direct_submission(token)
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
