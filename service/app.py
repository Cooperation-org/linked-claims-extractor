from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from pprint import pprint
from functools import wraps
from claim_extractor import ClaimExtractor
from backend_client.api_client import BackendAPIClient, PendingClaimsStore, require_backend_auth
import uuid

load_dotenv()

app = Flask(__name__)
CORS(app)

# Config
API_KEY = os.getenv('API_KEY')
BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:3000')

# Initialize components
PROMPT = """Here is a narrative about some work experience I had.  Please help me extract a list of skills and skill descriptions that an employer would recognize, that I could include in a resume. Try to find multiple skills, but ONLY list skills supported by the following work history:

"""

extractor = ClaimExtractor(schema_name='SIMPLE_SKILL')
pending_store = PendingClaimsStore()

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key and api_key == API_KEY:
            return f(*args, **kwargs)
        return jsonify({"error": "Invalid API key"}), 401
    return decorated

@app.route('/extract', methods=['POST'])
def process_text():
    """Extract claims from text - original endpoint for compatibility"""
    try:
        data = request.json
        text = data.get('text')

        if not text:
            return jsonify({"error": "No text provided"}), 400

        # Process with LangChain
        result = extractor.extract_claims(text, PROMPT)
        pprint(result)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/extract-with-approval', methods=['POST'])
@require_backend_auth
def extract_with_approval():
    """Extract claims and store for user approval"""
    try:
        data = request.json
        text = data.get('text')
        source_url = data.get('source_url')
        schema_name = data.get('schema_name', 'SIMPLE_SKILL')
        custom_prompt = data.get('prompt', PROMPT)
        
        if not text and not source_url:
            return jsonify({"error": "Either text or source_url must be provided"}), 400
        
        # Create extractor with specified schema
        custom_extractor = ClaimExtractor(schema_name=schema_name)
        
        # Extract claims
        if source_url:
            claims = custom_extractor.extract_claims_from_url(source_url)
            extracted_from = source_url
        else:
            claims = custom_extractor.extract_claims(text, custom_prompt)
            extracted_from = "user_provided_text"
        
        # Store for approval
        session_id = str(uuid.uuid4())  # In production, use actual session management
        approval_id = pending_store.store_pending_claims(
            session_id=session_id,
            claims=claims,
            extracted_from=extracted_from
        )
        
        return jsonify({
            "approval_id": approval_id,
            "claims": claims,
            "extracted_from": extracted_from,
            "total_claims": len(claims)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/pending-claims/<approval_id>', methods=['GET'])
@require_backend_auth
def get_pending_claims(approval_id):
    """Get pending claims for review"""
    try:
        claims_data = pending_store.get_pending_claims(approval_id)
        if not claims_data:
            return jsonify({"error": "Approval ID not found"}), 404
        
        return jsonify(claims_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/approve-claims', methods=['POST'])
@require_backend_auth
def approve_claims():
    """Approve and submit selected claims to backend"""
    try:
        data = request.json
        approval_id = data.get('approval_id')
        approved_indices = data.get('approved_indices', [])
        
        if not approval_id:
            return jsonify({"error": "approval_id is required"}), 400
        
        # Use the backend token from the request
        results = pending_store.approve_claims(
            approval_id=approval_id,
            approved_claim_ids=approved_indices,
            user_token=request.backend_token
        )
        
        return jsonify({
            "status": "success",
            "results": results
        })
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/submit-claims-direct', methods=['POST'])
@require_backend_auth
def submit_claims_direct():
    """Direct submission of claims to backend (bypass approval)"""
    try:
        data = request.json
        claims = data.get('claims', [])
        
        if not claims:
            return jsonify({"error": "No claims provided"}), 400
        
        # Submit to backend
        client = BackendAPIClient(
            base_url=BACKEND_API_URL,
            access_token=request.backend_token
        )
        
        results = client.batch_create_claims(claims)
        
        return jsonify({
            "status": "success",
            "results": results
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "linked-claims-extractor",
        "backend_url": BACKEND_API_URL
    })

if __name__ == '__main__':
    app.run(debug=True)
