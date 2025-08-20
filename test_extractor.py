#!/usr/bin/env python3
"""
Simple test script for the linked-claims-extractor
This script tests the basic functionality without requiring full installation
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the claim_extractor to the Python path
sys.path.insert(0, 'claim_extractor/src')

def test_basic_import():
    """Test if we can import the ClaimExtractor"""
    try:
        from claim_extractor import ClaimExtractor
        print("✅ Successfully imported ClaimExtractor")
        return True
    except ImportError as e:
        print(f"❌ Failed to import ClaimExtractor: {e}")
        return False

def test_claim_extraction():
    """Test basic claim extraction functionality"""
    try:
        from claim_extractor import ClaimExtractor
        
        # Check if we have an API key
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key or api_key == 'your_api_key_here':
            print("⚠️  No ANTHROPIC_API_KEY found. Skipping AI test.")
            print("   To test with real AI, set your Anthropic API key in .env file")
            return True
        
        # Initialize the extractor
        extractor = ClaimExtractor()
        
        # Test with simple text
        test_text = """
        The company reduced carbon emissions by 25% last year.
        We planted 500 trees in the local community.
        Our solar panels generated 50,000 kWh of clean energy.
        """
        
        print("🔄 Testing claim extraction...")
        claims = extractor.extract_claims(test_text)
        
        print(f"✅ Extracted {len(claims)} claims:")
        for i, claim in enumerate(claims, 1):
            print(f"   {i}. {claim}")
        
        return True
        
    except Exception as e:
        print(f"❌ Claim extraction test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing linked-claims-extractor setup...")
    print("=" * 50)
    
    # Test imports
    if not test_basic_import():
        return False
    
    # Test functionality
    if not test_claim_extraction():
        return False
    
    print("=" * 50)
    print("🎉 All tests completed successfully!")
    print("\nNext steps:")
    print("1. Set your ANTHROPIC_API_KEY in .env file for full testing")
    print("2. Try extracting claims from real documents")
    print("3. Integrate with LinkedTrust backend")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
