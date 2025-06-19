# LinkedClaims Extractor MVP Roadmap

## Overview

This roadmap outlines the implementation plan for the LinkedClaims Extractor MVP, taking into account the existing progress in the integration branch. The MVP will deliver a complete flow from PDF upload to validation, demonstrating the practical application of the LinkedClaims specification.

## Current Status (Integration Branch)

The integration branch already includes:
- Basic PDF text extraction functionality
- Initial claim identification logic
- LinkedTrust API client integration
- Flask-based demo application
- Authentication with the LinkedTrust backend

## Frontend Flow Design

### 1. PDF Upload & Processing
- **Simple Upload Interface**: Clean, single-page with drag-drop functionality
- **Processing Feedback**: Progress indicators during PDF parsing
- **Document Preview**: Display parsed content in reviewable chunks
- **Status**: Partially implemented, needs UI improvements

### 2. Claim Extraction & Review
- **Automatic Extraction**: NLP-based identification of claims from text
- **Interactive Review**: User-friendly interface to review, edit, and manage extracted claims
- **Batch Selection**: Allow users to select multiple claims for publishing
- **Status**: Basic extraction exists, needs better UI for review/editing

### 3. Claim Publishing
- **Authentication**: User authentication with LinkedTrust backend
- **Batch Publishing**: Send selected claims to the LinkedTrust API
- **Publish Feedback**: Clear success/failure indicators
- **Status**: API integration exists, needs better error handling and UI feedback

### 4. Validation Request Generation
- **Validator Selection**: Interface to specify validators for claims
- **Link Generation**: Create unique validation links for each claim
- **Communication Tools**: Templates for sharing validation requests
- **Status**: Not implemented yet

### 5. Validation Tracking
- **Status Dashboard**: View validation status of published claims
- **Response Collection**: Display validator feedback
- **Status**: Not implemented yet

## 3-Day Implementation Plan

### Day 1: Core Functionality & UI Improvements
1. Enhance PDF upload interface with better feedback
2. Improve claim extraction visualization
3. Add claim editing capabilities
4. Ensure proper authentication with dev.linkedtrust.us

### Day 2: Publishing & Validation Link Generation
1. Implement batch selection and publishing
2. Create validation link generation functionality
3. Develop email templates for validation requests
4. Build simple validation UI page

### Day 3: Validation Flow & Polish
1. Complete validation submission functionality
2. Add validation tracking dashboard
3. Polish UI for demonstration
4. Test end-to-end flow with real PDFs
5. Document usage and prepare demo materials

## Success Criteria
- Complete flow from PDF upload to claim validation
- Successfully extract at least 3 types of claims (funding, impact, etc.)
- Generate validation links that work on mobile devices
- Record validation responses back to LinkedTrust backend
- Clean, intuitive UI suitable for demonstration

## Next Steps (Post-MVP)
- Improve NLP for more accurate claim extraction
- Support additional document formats
- Add batch processing capabilities
- Implement dashboard for tracking validation statistics
- Integrate video testimonial capabilities