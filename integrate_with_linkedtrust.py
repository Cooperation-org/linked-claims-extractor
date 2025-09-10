#!/usr/bin/env python3
"""
Integration script that extracts claims from documents and submits them to LinkedTrust
"""

import sys
import json
import requests
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the claim_extractor to the Python path
sys.path.insert(0, 'claim_extractor/src')

from claim_extractor import ClaimExtractor

class LinkedTrustIntegrator:
    def __init__(self):
        self.extractor = ClaimExtractor()
        self.linkedtrust_api = "https://dev.linkedtrust.us/api"
        
    def extract_and_submit_claims(self, text, source_uri=None):
        """
        Extract claims from text and submit them to LinkedTrust
        """
        print("Extracting claims from text...")
        claims = self.extractor.extract_claims(text)
        
        if not claims:
            print("No claims found in text.")
            return []
        
        print(f"Extracted {len(claims)} claims. Converting to LinkedTrust format...")
        
        results = []
        for i, claim in enumerate(claims, 1):
            try:
                # Convert extracted claim to W3C Verifiable Credential format
                credential = self.create_verifiable_credential(claim, source_uri)
                
                # Submit to LinkedTrust
                response = self.submit_to_linkedtrust(credential)
                
                print(f"Claim {i}: {response.get('status', 'Unknown status')}")
                results.append({
                    'claim': claim,
                    'credential': credential,
                    'response': response
                })
                
            except Exception as e:
                print(f"Error processing claim {i}: {e}")
                results.append({
                    'claim': claim,
                    'error': str(e)
                })
        
        return results
    
    def create_verifiable_credential(self, claim, source_uri=None):
        """
        Convert extracted claim to W3C Verifiable Credential format for LinkedTrust
        """
        # Generate a simple issuer DID (in production, this would be properly managed)
        issuer_did = "did:example:claims-extractor"
        
        # Create the credential structure
        credential = {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://cooperation.org/credentials/v1"
            ],
            "type": ["VerifiableCredential", "LinkedClaim"],
            "issuer": issuer_did,
            "issuanceDate": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "credentialSubject": {
                "id": f"did:example:{claim.get('subject', 'unknown').lower().replace(' ', '')}",
                "claim": claim.get('claim', ''),
                "subject": claim.get('subject', ''),
                "statement": claim.get('statement', ''),
                "aspect": claim.get('aspect', ''),
                "effectiveDate": claim.get('effectiveDate'),
                "confidence": claim.get('confidence', 0),
                "howKnown": claim.get('howKnown', 'EXTRACTED')
            }
        }
        
        # Add quantitative data if present
        if claim.get('amt') is not None:
            credential["credentialSubject"]["amt"] = claim.get('amt')
            credential["credentialSubject"]["unit"] = claim.get('unit', '')
        
        # Add source information
        if source_uri or claim.get('sourceURI'):
            credential["credentialSubject"]["sourceURI"] = source_uri or claim.get('sourceURI')
        
        return credential
    
    def submit_to_linkedtrust(self, credential):
        """
        Submit credential to LinkedTrust backend
        """
        try:
            # Prepare the request payload
            payload = {
                "credential": credential,
                "schema": "LinkedClaim",
                "metadata": {
                    "displayHints": {
                        "primaryDisplay": "credentialSubject.statement",
                        "secondaryDisplay": "credentialSubject.aspect",
                        "showQuantity": True if credential["credentialSubject"].get("amt") else False
                    },
                    "tags": ["extracted-claim", credential["credentialSubject"].get("aspect", "").replace(":", "-")],
                    "visibility": "public"
                }
            }
            
            # Make the API request
            response = requests.post(
                f"{self.linkedtrust_api}/credentials",
                json=payload,
                headers={
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIxNzEiLCJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNzU1ODg5MDQ1LCJleHAiOjE3NTU4OTI2NDV9.8fEbqWQszhy8P3vIMSdFq_2Sult95RA26vI0tW5Zugw'
},
                timeout=30
            )
            
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                return {
                    'status': 'success',
                    'uri': result.get('uri', 'Unknown URI'),
                    'response': result
                }
            else:
                return {
                    'status': 'error',
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'error': f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': f"Unexpected error: {str(e)}"
            }

def main():
    """
    Main function to run the integration
    """
    print("LinkedTrust Claims Integration")
    print("=" * 40)
    
    integrator = LinkedTrustIntegrator()
    
    # Test with a document
    try:
        with open('test_document.txt', 'r') as f:
            text = f.read()
            
        print(f"Processing document: {len(text)} characters")
        
        # Extract and submit claims
        results = integrator.extract_and_submit_claims(
            text, 
            source_uri="file://test_document.txt"
        )
        
        # Summary
        print("\n" + "=" * 40)
        print("INTEGRATION SUMMARY")
        print("=" * 40)
        
        successful = len([r for r in results if r.get('response', {}).get('status') == 'success'])
        failed = len(results) - successful
        
        print(f"Total claims processed: {len(results)}")
        print(f"Successfully submitted: {successful}")
        print(f"Failed submissions: {failed}")
        
        # Show URIs for successful submissions
        for i, result in enumerate(results, 1):
            if result.get('response', {}).get('status') == 'success':
                uri = result['response'].get('uri', 'Unknown')
                claim_text = result['claim'].get('statement', '')[:60] + "..."
                print(f"  {i}. {uri}")
                print(f"     Claim: {claim_text}")
        
        if failed > 0:
            print(f"\nErrors encountered:")
            for i, result in enumerate(results, 1):
                if 'error' in result or result.get('response', {}).get('status') != 'success':
                    error = result.get('error') or result.get('response', {}).get('error', 'Unknown error')
                    print(f"  {i}. {error}")
        
    except FileNotFoundError:
        print("Error: test_document.txt not found. Please create this file first.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()