import requests
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import jwt
from functools import wraps
import time
from flask import request, jsonify

class BackendAPIClient:
    """Client for interacting with the trust claim backend API"""
    
    def __init__(self, base_url: str = None, access_token: str = None):
        self.base_url = base_url or os.getenv('BACKEND_API_URL', 'http://localhost:3000')
        self.access_token = access_token or os.getenv('BACKEND_ACCESS_TOKEN')
        self.session = requests.Session()
        if self.access_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}'
            })
    
    def authenticate(self, email: str, password: str) -> str:
        """Authenticate user and store access token"""
        response = self.session.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        self.access_token = data.get('accessToken')
        self.session.headers.update({
            'Authorization': f'Bearer {self.access_token}'
        })
        return self.access_token
    
    def create_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a claim to the backend"""
        # Ensure required fields
        required_fields = ['subject', 'claim']
        for field in required_fields:
            if field not in claim_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Add default values if not present
        claim_payload = {
            'subject': claim_data['subject'],
            'claim': claim_data['claim'],
            'object': claim_data.get('object'),
            'sourceURI': claim_data.get('sourceURI'),
            'howKnown': claim_data.get('howKnown', 'DERIVED'),
            'confidence': claim_data.get('confidence', 0.8),
            'statement': claim_data.get('statement'),
            'aspect': claim_data.get('aspect'),
            'effectiveDate': claim_data.get('effectiveDate', datetime.utcnow().isoformat())
        }
        
        response = self.session.post(
            f"{self.base_url}/api/claims",
            json=claim_payload
        )
        response.raise_for_status()
        return response.json()
    
    def batch_create_claims(self, claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Submit multiple claims"""
        results = []
        errors = []
        
        for claim in claims:
            try:
                result = self.create_claim(claim)
                results.append(result)
            except Exception as e:
                errors.append({
                    'claim': claim,
                    'error': str(e)
                })
        
        return {
            'successful': results,
            'failed': errors
        }
    
    def get_claim(self, claim_id: int) -> Dict[str, Any]:
        """Get a specific claim by ID"""
        response = self.session.get(f"{self.base_url}/api/claims/{claim_id}")
        response.raise_for_status()
        return response.json()
    
    def get_claims_by_subject(self, subject_uri: str, page: int = 1, limit: int = 50) -> Dict[str, Any]:
        """Get claims for a specific subject"""
        # Base64 encode the URI as the backend expects
        import base64
        encoded_uri = base64.b64encode(subject_uri.encode()).decode()
        
        response = self.session.get(
            f"{self.base_url}/api/claims/subject/{encoded_uri}",
            params={'page': page, 'limit': limit}
        )
        response.raise_for_status()
        return response.json()


class PendingClaimsStore:
    """Store claims pending user approval"""
    
    def __init__(self, storage_path: str = "./pending_claims"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    def store_pending_claims(self, session_id: str, claims: List[Dict[str, Any]], 
                           extracted_from: str = None) -> str:
        """Store claims for user approval"""
        import json
        import uuid
        
        approval_id = str(uuid.uuid4())
        data = {
            'approval_id': approval_id,
            'session_id': session_id,
            'claims': claims,
            'extracted_from': extracted_from,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'pending'
        }
        
        filepath = os.path.join(self.storage_path, f"{approval_id}.json")
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return approval_id
    
    def get_pending_claims(self, approval_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve pending claims by approval ID"""
        import json
        
        filepath = os.path.join(self.storage_path, f"{approval_id}.json")
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def approve_claims(self, approval_id: str, approved_claim_ids: List[int], 
                      user_token: str = None) -> Dict[str, Any]:
        """Mark specific claims as approved and submit them"""
        import json
        
        data = self.get_pending_claims(approval_id)
        if not data:
            raise ValueError(f"No pending claims found for approval_id: {approval_id}")
        
        if data['status'] != 'pending':
            raise ValueError(f"Claims already processed with status: {data['status']}")
        
        # Filter approved claims
        approved_claims = [
            claim for i, claim in enumerate(data['claims']) 
            if i in approved_claim_ids
        ]
        
        # Submit to backend
        client = BackendAPIClient(access_token=user_token)
        results = client.batch_create_claims(approved_claims)
        
        # Update status
        data['status'] = 'processed'
        data['processed_at'] = datetime.utcnow().isoformat()
        data['approved_claim_ids'] = approved_claim_ids
        data['submission_results'] = results
        
        filepath = os.path.join(self.storage_path, f"{approval_id}.json")
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return results


# Middleware for Flask to handle authentication
def require_backend_auth(f):
    """Decorator to ensure request has valid backend authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid authorization header"}), 401
        
        token = auth_header.split(' ')[1]
        # Store token in request context for use in the handler
        request.backend_token = token
        return f(*args, **kwargs)
    return decorated
