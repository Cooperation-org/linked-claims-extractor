# Impact Claims Integration Guide

## Overview

This guide explains how to use the linked-claims-extractor to publish impact measurements to LinkedTrust as LinkedClaims, utilizing the `amt` and `unit` fields for quantifiable impacts.

## Key Concepts

### Impact Claims as LinkedClaims

Impact measurements are published as LinkedClaims with:
- `claim`: "impact" (indicates this is an impact measurement)
- `amt`: Numerical amount of impact
- `unit`: Unit of measurement (e.g., "people", "tons CO2", "dollars")
- `aspect`: Type of impact (e.g., "impact:social", "impact:environmental:carbon")

### Future: Impact Credentials

While currently published as LinkedClaims, these impact measurements can evolve into ImpactCredentials - a specialized credential format for certified impact measurements. The LinkedClaim format provides the foundation for this evolution.

## Integration Steps

### 1. Install Dependencies

```bash
pip install linked-claims-extractor
```

### 2. Configure LinkedTrust API

Set environment variables:
```bash
export LINKEDTRUST_API_KEY="your-api-key"
export LINKEDTRUST_API_URL="https://live.linkedtrust.us/api"  # optional
```

### 3. Basic Usage

```python
from impact_claims_client import EnhancedLinkedTrustClient

# Initialize client
client = EnhancedLinkedTrustClient()

# Submit a single impact claim
response = client.submit_impact_claim(
    subject="Your Organization",
    statement="Provided education to underserved communities",
    amount=10000,
    unit="students",
    aspect="impact:social:education",
    source_uri="https://yourorg.com/impact-report-2024",
    confidence=0.9
)
```

### 4. Extract and Submit from Reports

```python
# Parse a PDF report
from claim_extractor import ClaimExtractor

extractor = ClaimExtractor()
claims = extractor.extract_from_pdf("impact_report.pdf")

# Convert to impact claims and submit
for claim in claims:
    if claim.get("type") == "impact":
        response = client.submit_impact_claim(
            subject=claim["subject"],
            statement=claim["statement"],
            amount=claim.get("amount"),
            unit=claim.get("unit"),
            aspect=claim.get("aspect", "impact:general"),
            source_uri=claim.get("source")
        )
```

## Impact Claim Types

### Social Impact
```python
client.submit_impact_claim(
    subject="Health Initiative",
    statement="Vaccinated children in rural areas",
    amount=50000,
    unit="children",
    aspect="impact:social:health"
)
```

### Environmental Impact
```python
client.submit_impact_claim(
    subject="Solar Project",
    statement="Reduced carbon emissions",
    amount=1000,
    unit="tons CO2",
    aspect="impact:environmental:carbon"
)
```

### Economic Impact
```python
client.submit_impact_claim(
    subject="Microfinance Program",
    statement="Provided small business loans",
    amount=5000000,
    unit="USD",
    aspect="impact:economic:finance"
)
```

## Best Practices

1. **Use Specific Aspects**: Use hierarchical aspects like "impact:social:education" for better categorization
2. **Include Source URIs**: Always reference the source report or document
3. **Consistent Units**: Use standard units for measurements
4. **Confidence Scores**: Provide realistic confidence scores based on data quality

## Future Roadmap

### ImpactCredential Format (Proposed)

```json
{
  "@context": ["https://www.w3.org/2018/credentials/v1", "https://linkedtrust.org/contexts/impact"],
  "type": ["VerifiableCredential", "ImpactCredential"],
  "credentialSubject": {
    "id": "did:web:organization.com",
    "impact": {
      "statement": "Reduced carbon emissions",
      "measurement": {
        "amount": 5000,
        "unit": "tons CO2"
      },
      "aspect": "environmental:carbon",
      "period": {
        "start": "2024-01-01",
        "end": "2024-12-31"
      },
      "methodology": "GHG Protocol"
    }
  }
}
```

This future format will:
- Support third-party verification
- Include methodology references
- Enable aggregation and comparison
- Maintain backward compatibility with LinkedClaims

## API Response Format

Successful submission returns:
```json
{
  "success": true,
  "claim": {
    "id": "https://linkedtrust.us/claims/123",
    "subject": "Organization Name",
    "claim": "impact",
    "amt": 10000,
    "unit": "people",
    "aspect": "impact:social"
  },
  "uri": "https://linkedtrust.us/claims/123"
}
```

## Error Handling

```python
try:
    response = client.submit_impact_claim(...)
except ValueError as e:
    print(f"Invalid claim format: {e}")
except requests.RequestException as e:
    print(f"API error: {e}")
```

## Support

For questions about impact claim formats or the LinkedTrust API, see:
- LinkedTrust Documentation: https://linkedtrust.org/docs
- Impact Measurement Standards: https://linkedtrust.org/impact
