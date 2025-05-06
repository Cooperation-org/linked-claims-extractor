"""
LinkedClaims Extractor Demo Application

This is a Flask web application that demonstrates the full workflow for extracting
claims from PDFs, validating them, signing them, and publishing them to LinkedTrust.
"""

import os
import json
import logging
import tempfile
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Import our modules
from pdf_parser.src.pdf_parser.pdf_processor import PDFProcessor
from claim_extractor import ClaimExtractor
from linkedtrust_client import LinkedTrustClient
from key_manager import KeyManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Initialize components
pdf_processor = PDFProcessor()
claim_extractor = ClaimExtractor()
key_manager = KeyManager()
linkedtrust_client = None  # Will be initialized with API key when needed

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the main application page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle PDF file upload."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Store the filepath in session for later processing
        return jsonify({
            "success": True, 
            "filename": filename,
            "filepath": filepath
        })
    else:
        return jsonify({"error": "Invalid file format. Please upload a PDF."}), 400

@app.route('/extract', methods=['POST'])
def extract_claims():
    """Extract claims from the uploaded PDF."""
    data = request.json
    filepath = data.get('filepath')
    
    if not filepath or not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    
    try:
        # Process PDF to extract text
        logger.info(f"Processing PDF: {filepath}")
        
        # Extract text from PDF pages
        page_texts = []
        try:
            # Use page-by-page extraction
            page_texts = pdf_processor.extract_text_from_pdf_per_page(filepath)
            logger.info(f"Extracted {len(page_texts)} pages of text")
        except Exception as e:
            logger.error(f"Error in page extraction: {str(e)}")
            # Fall back to whole document extraction
            try:
                full_text = pdf_processor.extract_text_from_pdf(filepath)
                page_texts = [{"0": full_text['cleaned_text']}]
                logger.info("Extracted text using fallback method")
            except Exception as e2:
                logger.error(f"Failed to extract text: {str(e2)}")
                return jsonify({"error": f"Failed to extract text: {str(e2)}"}), 500
        
        # Extract claims from each page
        all_claims = []
        for i, page_dict in enumerate(page_texts):
            page_num = list(page_dict.keys())[0]
            text = list(page_dict.values())[0]
            
            # Skip pages with very little text
            if len(text.strip()) < 50:
                continue
                
            logger.info(f"Extracting claims from page {page_num}")
            try:
                page_claims = claim_extractor.extract_claims(text)
                
                # Add page number and source to claims
                for claim in page_claims:
                    claim['page'] = int(page_num)
                    claim['sourceText'] = text
                    if 'howKnown' not in claim:
                        claim['howKnown'] = 'WEB_DOCUMENT'
                
                all_claims.extend(page_claims)
                logger.info(f"Extracted {len(page_claims)} claims from page {page_num}")
            except Exception as e:
                logger.error(f"Error extracting claims from page {page_num}: {str(e)}")
        
        # Add unique IDs to claims
        for i, claim in enumerate(all_claims):
            claim['id'] = i + 1
        
        return jsonify({
            "success": True,
            "claims": all_claims,
            "total": len(all_claims)
        })
        
    except Exception as e:
        logger.error(f"Error in claim extraction: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/sign', methods=['POST'])
def sign_claims():
    """Sign the selected claims."""
    data = request.json
    claims = data.get('claims', [])
    
    if not claims:
        return jsonify({"error": "No claims provided"}), 400
    
    try:
        # Ensure keys exist
        private_key, public_key = key_manager.ensure_keys_exist()
        
        # Sign each claim
        signed_claims = []
        for claim in claims:
            # Remove non-essential fields from the claim
            clean_claim = {k: v for k, v in claim.items() if k not in ['id', 'page', 'sourceText']}
            
            # Sign the claim
            signed_claim = key_manager.sign_claim(clean_claim)
            
            # Add original ID for reference
            signed_claim['original_id'] = claim.get('id')
            signed_claims.append(signed_claim)
        
        return jsonify({
            "success": True,
            "signed_claims": signed_claims,
            "total": len(signed_claims)
        })
        
    except Exception as e:
        logger.error(f"Error signing claims: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/publish', methods=['POST'])
def publish_claims():
    """Publish the signed claims to LinkedTrust."""
    data = request.json
    api_key = data.get('api_key')
    endpoint = data.get('endpoint', 'https://live.linkedtrust.us/api')
    claims = data.get('claims', [])
    
    if not api_key:
        return jsonify({"error": "API key is required"}), 400
    
    if not claims:
        return jsonify({"error": "No claims provided"}), 400
    
    try:
        # Initialize LinkedTrust client with provided API key
        global linkedtrust_client
        linkedtrust_client = LinkedTrustClient(api_key=api_key, api_url=endpoint)
        
        # Submit claims in batch
        results = linkedtrust_client.submit_claims_batch(claims)
        
        # Count successes and failures
        success_count = sum(1 for r in results if r.get('success', False))
        failure_count = len(results) - success_count
        
        return jsonify({
            "success": True,
            "results": results,
            "summary": {
                "total": len(results),
                "success": success_count,
                "failure": failure_count
            }
        })
        
    except Exception as e:
        logger.error(f"Error publishing claims: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/validate', methods=['POST'])
def validate_claims():
    """Validate the extracted claims."""
    data = request.json
    claims = data.get('claims', [])
    
    if not claims:
        return jsonify({"error": "No claims provided"}), 400
    
    try:
        # Validate each claim
        validation_results = []
        for claim in claims:
            # Start with a copy of the claim
            result = claim.copy()
            
            # Check required fields
            required_fields = ["subject", "claim", "statement"]
            missing_fields = [field for field in required_fields if field not in claim or not claim[field]]
            
            # Check valid claim type
            valid_claim_types = ["impact", "rated", "same_as"]
            valid_claim_type = claim.get("claim") in valid_claim_types
            
            # Add validation results
            result["validation"] = {
                "missing_fields": missing_fields,
                "valid_claim_type": valid_claim_type,
                "is_valid": len(missing_fields) == 0 and valid_claim_type
            }
            
            validation_results.append(result)
        
        # Count valid and invalid claims
        valid_count = sum(1 for r in validation_results if r["validation"]["is_valid"])
        invalid_count = len(validation_results) - valid_count
        
        return jsonify({
            "success": True,
            "validated_claims": validation_results,
            "summary": {
                "total": len(validation_results),
                "valid": valid_count,
                "invalid": invalid_count
            }
        })
        
    except Exception as e:
        logger.error(f"Error validating claims: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/cleanup', methods=['POST'])
def cleanup():
    """Clean up temporary files."""
    data = request.json
    filepath = data.get('filepath')
    
    if filepath and os.path.exists(filepath):
        try:
            os.remove(filepath)
            return jsonify({"success": True, "message": "File deleted"})
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"success": True, "message": "Nothing to clean up"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
