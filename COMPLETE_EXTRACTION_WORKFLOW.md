\# Complete Claims Extraction to LinkedTrust Workflow



\## Overview



This guide documents the complete process for extracting structured claims from documents and integrating them with the LinkedTrust ecosystem. It covers setup, usage, testing, and integration steps.



\## Prerequisites



\- Python 3.8+

\- Git

\- Anthropic API account with billing enabled

\- Access to LinkedTrust development environment



\## Initial Setup



\### 1. Repository Setup



```bash

\# Fork the repository on GitHub

\# Clone your fork

git clone https://github.com/YOUR\_USERNAME/linked-claims-extractor.git

cd linked-claims-extractor



\# Add upstream remote

git remote add upstream https://github.com/Cooperation-org/linked-claims-extractor.git

```



\### 2. Environment Configuration



```bash

\# Create virtual environment

python -m venv venv



\# Activate (Windows)

venv\\Scripts\\activate



\# Install dependencies

pip install langchain langchain-anthropic python-dotenv requests

```



\### 3. Environment Variables



Create `.env` file:

```

ANTHROPIC\_API\_KEY=your\_api\_key\_here

CLAUDE\_MODEL=claude-3-5-sonnet-20241022

CLAUDE\_MAX\_TOKENS=4096

```



\### 4. Verification Test



Create and run `test\_extractor.py`:

```bash

python test\_extractor.py

```



\## Claims Extraction Process



\### Understanding the Schema



The system uses `linked\_trust.json` schema with these key fields:

\- `subject`: Entity the claim is about

\- `claim`: Type ("impact", "rated", "same\_as")

\- `aspect`: Category (impact:financial, impact:social, impact:environmental)

\- `statement`: Concise narrative from text

\- `amt`/`unit`: Quantitative data if present

\- `confidence`: Extraction confidence (0-1)

\- `effectiveDate`: When the impact occurred



\### Basic Extraction



```python

from claim\_extractor import ClaimExtractor

from dotenv import load\_dotenv



load\_dotenv()

extractor = ClaimExtractor()



\# Extract from text

claims = extractor.extract\_claims(your\_text)



\# Extract from URL

claims = extractor.extract\_claims\_from\_url(url)

```



\### Testing Different Document Types



The extractor handles multiple domains effectively:



\*\*Financial Claims\*\* (7 claims typically extracted):

\- Revenue, cost savings, market share

\- Aspect: impact:financial, impact:market

\- Units: USD, percentages



\*\*Social Impact\*\* (6 claims typically extracted):

\- Education, employment, community programs

\- Aspect: impact:social, impact:work

\- Units: people, percentages



\*\*Environmental Data\*\* (6 claims typically extracted):

\- Energy, water, waste, emissions

\- Aspect: impact:environmental

\- Units: kWh, gallons, tons, trees



\## LinkedTrust Integration



\### Credential Format Conversion



Extracted claims are converted to W3C Verifiable Credentials:



```python

credential = {

&nbsp;   "@context": \[

&nbsp;       "https://www.w3.org/2018/credentials/v1",

&nbsp;       "https://cooperation.org/credentials/v1"

&nbsp;   ],

&nbsp;   "type": \["VerifiableCredential", "LinkedClaim"],

&nbsp;   "issuer": "did:example:claims-extractor",

&nbsp;   "issuanceDate": datetime.utcnow().isoformat() + "Z",

&nbsp;   "credentialSubject": {

&nbsp;       # Claim data here

&nbsp;   }

}

```



\### API Submission



```python

response = requests.post(

&nbsp;   "https://dev.linkedtrust.us/api/credentials",

&nbsp;   json={

&nbsp;       "credential": credential,

&nbsp;       "schema": "LinkedClaim",

&nbsp;       "metadata": {

&nbsp;           "displayHints": {...},

&nbsp;           "tags": \[...],

&nbsp;           "visibility": "public"

&nbsp;       }

&nbsp;   }

)

```



\### Full Integration Script



Use `integrate\_with\_linkedtrust.py` for end-to-end processing:

```bash

python integrate\_with\_linkedtrust.py

```



\## Common Issues and Solutions



\### Dependency Conflicts



\*\*Problem\*\*: Conflicting package versions between spacy/thinc

\*\*Solution\*\*: Install minimal dependencies only:

```bash

pip install langchain langchain-anthropic python-dotenv requests

```



\### API Authentication



\*\*Problem\*\*: 401 "No token provided" errors

\*\*Solution\*\*: Contact supervisor for LinkedTrust API credentials



\### Model Name Errors



\*\*Problem\*\*: 404 model not found

\*\*Solution\*\*: Update to current model names in .env:

```

CLAUDE\_MODEL=claude-3-5-sonnet-20241022

```



\### Virtual Environment Issues



\*\*Problem\*\*: "No module named langchain"

\*\*Solution\*\*: Ensure virtual environment is activated:

```bash

venv\\Scripts\\activate

```



\## Performance Benchmarks



\### Extraction Accuracy

\- Financial claims: ~7 claims per document, 0.9 confidence

\- Social impact: ~6 claims per document, 0.9 confidence  

\- Environmental: ~6 claims per document, 0.9 confidence



\### Supported Data Types

\- Monetary values (USD, various currencies)

\- Percentages and ratios

\- Quantities (people, trees, vehicles)

\- Energy units (kWh, MW)

\- Environmental metrics (tons CO2, gallons)



\## Development Workflow



\### Creating Improvements



1\. Create feature branch:

```bash

git checkout -b feature/improvement-name

```



2\. Make changes and test

3\. Commit with descriptive messages

4\. Push and create pull request



\### Testing New Features



Create test files for different domains:

\- `test\_financial\_claims.txt`

\- `test\_social\_impact.txt` 

\- `test\_environmental\_data.txt`



Run extraction tests and compare results.



\## Future Enhancements



\### Potential Improvements

\- Batch processing for multiple documents

\- Enhanced error handling and retry logic

\- PDF parsing integration

\- Real-time API authentication

\- Automated testing suite

\- Custom schema support



\### Integration Opportunities

\- Direct PDF upload processing

\- Web interface for document submission

\- Dashboard for extraction monitoring

\- Export to multiple formats



\## Troubleshooting



\### Debug Mode

Add logging to see detailed processing:

```python

import logging

logging.basicConfig(level=logging.DEBUG)

```



\### API Testing

Test API connectivity without credentials:

```bash

curl https://dev.linkedtrust.us/api/health

```



\### File Issues

Ensure file encoding is UTF-8 for text documents.



\## Support and Resources



\- Repository: https://github.com/Cooperation-org/linked-claims-extractor

\- LinkedTrust API: https://dev.linkedtrust.us/api/docs/

\- Anthropic Console: https://console.anthropic.com/



\## Contributing



See DEVELOPMENT\_SETUP.md for local development guidelines and common setup issues.

