# Roadmap

## Phase 1: Core Library Enhancement
- Add LinkedTrust publishing to claim_extractor
  - Default endpoint: https://live.linkedtrust.us/api
  - Allow endpoint override
  - Include sourceURI parameter for document source
- Add auth instructions (Google OAuth via LinkedTrust)
- Consider browser vs backend auth flow

## Phase 2: Service Refactoring
- Refactor extraction-service to use claim_extractor for publishing
- Remove duplicate LinkedTrust client code
- Ensure service handles PDF ingestion, extraction delegated to library

## Phase 3: Convenience Methods
- Add claim cleaning/validation utilities
- Support multiple input formats beyond raw text
- Extract common patterns from talent repo and other consumers

## Next Priority: Fix Extraction Service
1. Make service locally testable
2. Add proper test suite
3. Ensure PDF processing works end-to-end
4. Document local development setup