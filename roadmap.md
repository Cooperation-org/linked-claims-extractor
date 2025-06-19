# LinkedClaims Extractor Frontend Flow

## Overview
This roadmap outlines the user flow for the LinkedClaims Extractor frontend, designed to extract verifiable claims from PDF documents and facilitate validation through the LinkedTrust platform.

## Flow Design

### 1. PDF Upload & Processing

- **Simple Upload Interface**: Single-page with drag-drop and file select
  - Clean, minimal design with clear instructions
  - Support for multiple file formats (primarily PDF)

- **Processing Feedback**: Clear indication of PDF parsing progress
  - Progress bar showing parsing status
  - Cancel option for large documents

- **Document Preview**: Show the parsed content in chunks for review
  - Collapsible sections by page or logical divisions
  - Highlight potential claims in the text

### 2. Claim Extraction & Review

- **Automatic Extraction**: System identifies potential claims using NLP/patterns
  - Focus on funding amounts, impact metrics, and program descriptions
  - Confidence scoring for each extracted claim

- **Interactive Review**: User can:
  - View each extracted claim
  - Edit claim details if needed
  - Add manual claims for items missed by automation
  - Delete false positives

- **Batch Operations**: Select multiple claims for publishing
  - Bulk edit capabilities for common fields
  - Filtering and sorting options

### 3. Claim Publishing

- **Authentication**: Connect to LinkedTrust account
  - Simple login/token authorization
  - Remember session for repeat usage

- **Batch Publish**: Send selected claims to LinkedTrust backend
  - Preview of claims before final submission
  - Option to save draft claims for later

- **Publish Feedback**: Show success/failure status for each claim
  - Clear success/error messages
  - Retry options for failed submissions

### 4. Validation Request Generation

- **Validator Selection**: Enter email addresses for validators
  - Import contacts or manual entry
  - Group validators by role or relationship to claim

- **Link Generation**: Create unique validation links for each claim
  - Secure, time-limited validation URLs
  - Preview of validation page

- **Communication**: Send validation requests via email or generate shareable links
  - Customizable email templates
  - Copy-paste links for manual sharing

### 5. Validation Tracking

- **Status Dashboard**: View validation status of published claims
  - Visual indicators of validation progress
  - Filtering by validation status

- **Response Collection**: Collect and display validator responses
  - Aggregate validation results
  - Display individual validator feedback

- **Feedback Incorporation**: Update claim status based on validations
  - Confidence scoring adjusted by validations
  - Flag conflicting validations for review

## Implementation Priority

For the 3-day MVP development:

1. **Day 1**: PDF Upload, Processing, and Basic Claim Extraction
   - Implement file upload and parsing
   - Basic claim identification logic
   - Simple claim display

2. **Day 2**: Claim Review, Editing, and Publishing
   - Claim editing interface
   - Integration with LinkedTrust API
   - Publishing functionality

3. **Day 3**: Validation Flow and Polish
   - Validation link generation
   - Email template for validators
   - Simple validation page
   - Final testing and bug fixes

## Success Criteria

The MVP should demonstrate:

1. Successfully extracting at least 3 types of claims from a sample PDF
2. Publishing claims to the LinkedTrust backend
3. Generating validation links that can be shared with validators
4. Collecting and displaying validation responses

This implementation focuses on creating a functional end-to-end flow rather than perfecting each component, allowing for rapid demonstration and feedback.