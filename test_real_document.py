import sys
sys.path.insert(0, 'claim_extractor/src')
from claim_extractor import ClaimExtractor
from dotenv import load_dotenv

load_dotenv()

extractor = ClaimExtractor()
filename = input("Enter filename to test: ")
with open(filename, 'r') as f:
    text = f.read()
    
claims = extractor.extract_claims(text)
print(f'Extracted {len(claims)} claims:')
for i, claim in enumerate(claims, 1):
    print(f'{i}. {claim}')