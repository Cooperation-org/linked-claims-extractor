# LinkedClaims Extractor Project Guide

## Overview

This project creates a system to extract structured claims from the Gates Foundation's year-end report and publish them to the LinkedTrust platform (live.linkedtrust.us). This guide provides instructions for team members working with Claude to implement this project.

## Project Components

The repository has several key components:

1. **PDF Parser** (`/pdf_parser`)
   - Processes PDF documents and extracts text
   - Can process text page-by-page or as a whole document
   - Handles text extraction and maintains page context

2. **Claim Extractor** (`/claim_extractor`)
   - Uses Claude to identify and extract structured claims
   - Formats claims according to LinkedTrust schema
   - Validates claims against requirements

3. **LinkedTrust Client** (`/linkedtrust_client.py`)
   - Handles API authentication
   - Formats and submits claims to LinkedTrust
   - Manages error handling and responses

4. **Key Manager** (`/key_manager.py`)
   - Handles cryptographic key generation and management
   - Signs claims with private keys
   - Verifies signatures before submission

5. **Demo App** (`/demo_app.py` and `/templates`)
   - Web application to demonstrate the full workflow
   - Allows uploading PDFs, extracting claims, and publishing to LinkedTrust
   - Provides UI for reviewing and validating claims

## Architecture

The system follows this workflow:

1. PDF → PDF Parser → Extracted Text
2. Extracted Text → Claim Extractor → Structured Claims
3. Structured Claims → Validation → Valid Claims
4. Valid Claims → Key Manager → Signed Claims
5. Signed Claims → LinkedTrust Client → Published Claims

## Implementation Status

- **PDF Parser**: Implemented, needs refinement
- **Claim Extractor**: Basic implementation exists, needs prompt improvements
- **Key Manager**: Implemented
- **LinkedTrust Client**: Implemented
- **Demo App**: Basic implementation, needs integration testing

## Next Steps

1. **Refine PDF Parser**
   - Improve text segmentation for Gates Foundation reports
   - Better handle page boundaries and context

2. **Enhance Claim Extraction**
   - Optimize Claude prompts for better claim identification
   - Improve handling of dates, numbers, and uncertainty

3. **Integrate Components**
   - Connect all modules in the demo application
   - Ensure proper error handling and validation

4. **Test with Real PDFs**
   - Use actual Gates Foundation reports
   - Fine-tune based on real-world extraction results

5. **Polish Demo UI**
   - Improve UX for the review interface
   - Add helpful context and explanations

## Working with Claude

When working with Claude on this project:

1. **PDF Processing**: Ask Claude to help optimize the PDF parser for Gates Foundation report formats.

2. **Prompt Engineering**: Collaborate with Claude to refine prompts for accurate claim extraction.

3. **Schema Understanding**: Claude understands the LinkedTrust schema and can help validate claim structures.

4. **Code Generation**: Claude can write or improve code for any component of the system.

5. **Testing**: Claude can help design test cases and analyze extraction results.

## LinkedTrust Schema

Claims must follow this schema:

```json
{
  "subject": "string",       // Entity the claim is about
  "claim": "string",         // Type: "impact", "rated", or "same_as"
  "object": "string",        // Optional: typically a URL
  "statement": "string",     // The exact claim text
  "aspect": "string",        // Category (e.g., "impact:social")
  "amt": 0,                  // Optional: numerical amount for impact claims
  "unit": "string",          // Optional: units for the amount
  "effectiveDate": "date",   // When the claim occurred
  "confidence": 0,           // Confidence score (0-1)
  "sourceURI": "string"      // Source document
}
```

## Examples

### Example of a Gates Foundation Impact Claim

```json
{
  "subject": "Gates Foundation",
  "claim": "impact",
  "statement": "The Gates Foundation's vaccination program reached more than 10 million children across developing countries in 2019.",
  "aspect": "impact:social",
  "amt": 10000000,
  "unit": "children",
  "effectiveDate": "2019-12-31T00:00:00Z",
  "confidence": 0.95,
  "howKnown": "WEB_DOCUMENT"
}
```

### Example of a Rating Claim

```json
{
  "subject": "Gates Foundation Program",
  "claim": "rated",
  "statement": "The program was rated highly effective by independent evaluators.",
  "aspect": "quality:overall",
  "stars": 5,
  "score": 1.0,
  "effectiveDate": "2020-06-15T00:00:00Z",
  "confidence": 0.85,
  "howKnown": "WEB_DOCUMENT"
}
```

## Demo Preparation

For the Matt Gee demonstration:

1. Use the 2024 Gates Foundation Goalkeepers report
2. Extract at least 10 high-quality claims
3. Ensure at least 5 different types of claims (financial impact, social impact, ratings, etc.)
4. Create a smooth demo flow from upload to publishing
5. Prepare to explain how Claude helps identify claims

## Getting Started

1. Make sure you have the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key
   LINKEDTRUST_API_KEY=your_linkedtrust_api_key
   ```

3. Run the demo application:
   ```
   python demo_app.py
   ```

4. Access the UI at http://localhost:5000

## Resources

- [LinkedTrust API Documentation](https://live.linkedtrust.us/api/docs/)
- [Gates Foundation Goalkeepers Report](https://www.gatesfoundation.org/goalkeepers/report/)
- [Anthropic Claude Documentation](https://docs.anthropic.com/)
