# Linked Claims Extractor - Backend Integration

This document describes the integration between the linked-claims-extractor service and the trust-claim-backend API.

## Quick Start

1. **Environment Setup**
   ```bash
   cd linked-claims-extractor/service
   
   # Create .env file with:
   echo "API_KEY=your-extractor-api-key" >> .env
   echo "BACKEND_API_URL=http://localhost:3000" >> .env
   echo "ANTHROPIC_API_KEY=your-anthropic-key" >> .env
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Service**
   ```bash
   python app.py
   ```

## API Endpoints

### 1. Extract with Approval Flow (Recommended)
```bash
# Extract claims and store for approval
curl -X POST http://localhost:5000/extract-with-approval \
  -H "Authorization: Bearer YOUR_BACKEND_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I worked as a software engineer...",
    "schema_name": "SIMPLE_SKILL"
  }'

# Response:
{
  "approval_id": "uuid-here",
  "claims": [...],
  "extracted_from": "user_provided_text",
  "total_claims": 5
}
```

### 2. Review Pending Claims
```bash
curl -X GET http://localhost:5000/pending-claims/{approval_id} \
  -H "Authorization: Bearer YOUR_BACKEND_JWT_TOKEN"
```

### 3. Approve and Submit Claims
```bash
curl -X POST http://localhost:5000/approve-claims \
  -H "Authorization: Bearer YOUR_BACKEND_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "approval_id": "uuid-here",
    "approved_indices": [0, 2, 3]
  }'
```

### 4. Direct Submission (No Approval)
```bash
curl -X POST http://localhost:5000/submit-claims-direct \
  -H "Authorization: Bearer YOUR_BACKEND_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "claims": [
      {
        "subject": "https://example.com/user/123",
        "claim": "has_skill",
        "object": "Python Programming",
        "confidence": 0.9
      }
    ]
  }'
```

## Authentication Flow

1. **Get JWT Token from Backend**
   ```bash
   curl -X POST http://localhost:3000/auth/login \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "password": "password"
     }'
   ```

2. **Use Token in Extractor Requests**
   - Add header: `Authorization: Bearer YOUR_JWT_TOKEN`

## Integration Architecture

```
Frontend ─────┐
              ├─> Trust Claim Backend ─> Database
              │         ↑
              │         │ JWT Auth
              │         │
              └─> Extractor Service
                       │
                       └─> Pending Claims Store
```

## Deployment Considerations

1. **Security**
   - Always use HTTPS in production
   - Store API keys securely
   - Implement rate limiting

2. **Storage**
   - Pending claims are stored in `./pending_claims` directory
   - Consider using Redis or database for production

3. **Scaling**
   - Service is stateless except for pending claims
   - Can run multiple instances with shared storage

## Troubleshooting

1. **Authentication Errors**
   - Ensure JWT token is valid and not expired
   - Check BACKEND_API_URL is correct

2. **Extraction Errors**
   - Verify ANTHROPIC_API_KEY is set
   - Check schema_name is valid

3. **Backend Connection**
   - Ensure backend is running on specified port
   - Check network connectivity

## Next Steps

1. **Frontend Integration**
   - Build UI for claim review/approval
   - Add batch extraction support

2. **Enhanced Features**
   - Add PDF extraction support
   - Implement claim editing before approval
   - Add claim confidence thresholds

3. **Production Ready**
   - Add proper logging
   - Implement retry logic
   - Add monitoring/metrics
