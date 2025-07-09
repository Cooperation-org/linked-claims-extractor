from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
import json
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
import requests
from dotenv import load_dotenv
import logging

# Import your existing modules
from claim_extractor import ClaimExtractor
from pdf_parser import DocumentManager

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 80 * 1024 * 1024  # 80MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Storage for extracted claims
extracted_claims = {}

def validate_configuration():
    """Validate all required environment variables"""
    required_vars = {
        'LINKEDTRUST_EMAIL': 'LinkedTrust email for authentication',
        'LINKEDTRUST_PASSWORD': 'LinkedTrust password for authentication', 
        'ANTHROPIC_API_KEY': 'Claude API key for claim extraction',
        'FLASK_SECRET_KEY': 'Flask secret key for session security'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"  - {var}: {description}")
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        print("\n".join(missing_vars))
        print("\nPlease add these to your .env file")
        return False
    
    return True

class LinkedTrustAuth:
    def __init__(self):
        self.base_url = os.getenv('LINKEDTRUST_BASE_URL', 'https://dev.linkedtrust.us')
        self.email = os.getenv('LINKEDTRUST_EMAIL')
        self.password = os.getenv('LINKEDTRUST_PASSWORD')
        self.access_token = None
        self.refresh_token = None
        self.user_info = None
        self.login_time = None
        
        if not self.email or not self.password:
            raise ValueError("LINKEDTRUST_EMAIL and LINKEDTRUST_PASSWORD environment variables are required")
    
    def auto_login(self):
        """Auto login using environment variables"""
        return self.login(self.email, self.password)
    
    def login(self, email: str, password: str):
        """Login to LinkedTrust API"""
        url = f"{self.base_url}/auth/login"
        payload = {"email": email, "password": password}
        
        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("accessToken")
                self.refresh_token = data.get("refreshToken")
                self.user_info = data.get("user")
                self.login_time = datetime.now().isoformat()
                
                return {"success": True, "message": "Login successful", "data": data}
            else:
                return {"success": False, "error": f"Login failed with status {response.status_code}", "details": response.text}
                
        except requests.RequestException as e:
            return {"success": False, "error": f"Request failed: {str(e)}"}
    
    def get_auth_headers(self):
        """Get authorization headers, auto-login if needed"""
        if not self.access_token:
            result = self.auto_login()
            if not result["success"]:
                raise Exception(f"Auto-login failed: {result['error']}")
        
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def is_authenticated(self):
        """Check if we have a valid access token"""
        return bool(self.access_token)
    
    def create_claim(self, claim_data):
        """Create a new claim"""
        url = f"{self.base_url}/api/v4/claims"
        
        try:
            response = requests.post(url, json=claim_data, headers=self.get_auth_headers())
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return {"success": True, "data": response_data}
                except json.JSONDecodeError:
                    return {"success": True, "data": {"response": response.text}}
            elif response.status_code == 201:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Failed to create claim: {response.status_code}", "details": response.text}
                
        except Exception as e:
            return {"success": False, "error": f"Request failed: {str(e)}"}

# Validate configuration before starting
if not validate_configuration():
    exit(1)

# Initialize LinkedTrust client
try:
    auth_client = LinkedTrustAuth()
    print("✅ LinkedTrust API configured successfully")
except ValueError as e:
    logger.error(f"LinkedTrust configuration error: {e}")
    auth_client = None

# Test Claude API connection
try:
    test_extractor = ClaimExtractor()
    print("✅ Claude API configured successfully")
    claude_api_configured = True
except Exception as e:
    print(f"❌ Claude API configuration error: {e}")
    claude_api_configured = False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def _process_pdf(docmgr, pdf_path):
    """Process PDF and extract claims"""
    try:
        extractor = ClaimExtractor()
        
        # Extract page by page text
        page_texts = docmgr.process_pdf_all_or_pages(pdf_path, type="pages")
        page_texts_with_claims = []
        
        for page_dict in page_texts:
            page_num = list(page_dict.keys())[0]
            text = list(page_dict.values())[0]
            page_text_claims = extractor.extract_claims(text)
            
            for claim in page_text_claims:
                if 'howKnown' in claim.keys():
                    claim['howKnown'] = 'WEB_DOCUMENT'
            
            page_texts_with_claims.append((text, page_text_claims))
        
        return page_texts_with_claims
    
    except Exception as e:
        logger.error(f"Error in claim extraction: {str(e)}")
        raise Exception(f"Claim extraction failed: {str(e)}. Please check your Claude API configuration.")

@app.route('/')
def index():
    """Main page - Upload File"""
    return render_template('upload.html')

@app.route('/claims')
def view_claims():
    """View Claims page"""
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    search_query = request.args.get('search', '')
    
    # Filter and search claims
    filtered_claims = {}
    total_count = 0
    
    for claim_id, data in extracted_claims.items():
        claims = data['claims']
        
        # Apply status filter
        if status_filter == 'draft':
            claims = [c for c in claims if c.get('status', 'draft') == 'draft']
        elif status_filter == 'published':
            claims = [c for c in claims if c.get('status', 'draft') == 'published']
        
        # Apply search filter
        if search_query:
            claims = [c for c in claims if search_query.lower() in json.dumps(c).lower()]
        
        if claims:
            filtered_claims[claim_id] = {
                **data,
                'claims': claims
            }
            total_count += len(claims)
    
    return render_template('claims.html', 
                         extracted_claims=filtered_claims, 
                         total_count=total_count,
                         status_filter=status_filter,
                         search_query=search_query)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and process PDF"""
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        try:
            # Check Claude API configuration
            if not claude_api_configured:
                flash('Claude API not configured. Please check your ANTHROPIC_API_KEY.')
                return redirect(request.url)
            
            # Save uploaded file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Process PDF and extract claims
            try:
                docmgr = DocumentManager()
                page_texts_with_claims = _process_pdf(docmgr, file_path)
                
                # Generate unique claim ID
                claim_id = str(uuid.uuid4())
                
                # Flatten claims from all pages
                all_claims = []
                claim_index = 0
                for page_text, page_claims in page_texts_with_claims:
                    for claim in page_claims:
                        claim['status'] = 'draft'  # Set initial status
                        claim['page_text'] = page_text[:200] + '...' if len(page_text) > 200 else page_text
                        claim['claim_index'] = claim_index  # Add unique index for individual publishing
                        all_claims.append(claim)
                        claim_index += 1
                
                # Store extracted claims
                extracted_claims[claim_id] = {
                    'id': claim_id,
                    'filename': filename,
                    'original_filename': file.filename,
                    'file_path': file_path,
                    'upload_time': datetime.now().isoformat(),
                    'claims': all_claims,
                    'total_claims': len(all_claims)
                }
                
                flash(f'Successfully extracted {len(all_claims)} claims from {filename}')
                logger.info(f"Extracted {len(all_claims)} claims from {filename}")
                
                return redirect(url_for('view_claims'))
                
            except Exception as extraction_error:
                logger.error(f"Error extracting claims from {filename}: {str(extraction_error)}")
                flash(f'Error extracting claims: {str(extraction_error)}')
                return redirect(request.url)
            
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {str(e)}")
            flash(f'Error processing file: {str(e)}')
            return redirect(request.url)
    else:
        flash('Invalid file type. Only PDF files are allowed.')
        return redirect(request.url)

@app.route('/api/claims/<claim_id>/publish', methods=['POST'])
def publish_claims_to_linkedtrust(claim_id):
    """API endpoint to publish ALL claims to LinkedTrust"""
    if claim_id not in extracted_claims:
        return jsonify({'success': False, 'error': 'Claims not found'}), 404
    
    if not auth_client:
        return jsonify({'success': False, 'error': 'LinkedTrust not configured'}), 500
    
    try:
        claims_data = extracted_claims[claim_id]
        
        # Ensure we're authenticated with LinkedTrust
        if not auth_client.is_authenticated():
            auth_result = auth_client.auto_login()
            if not auth_result["success"]:
                return jsonify({
                    'success': False, 
                    'error': 'Failed to authenticate with LinkedTrust',
                    'details': auth_result["error"]
                }), 401
        
        published_claims = []
        failed_claims = []
        
        for claim in claims_data['claims']:
            if claim.get('status') == 'draft':
                try:
                    # Transform the claim data to LinkedTrust format - FIXED null values
                    inkedtrust_payload = {
                        "subject": claim.get('subject', None),
                        "claim": claim.get('claim', claim.get('type', 'Impact')),
                        "object": claim.get('object', claim.get('description', None)),
                        "statement": claim.get('statement', claim.get('description', None)),
                        "aspect": claim.get('aspect', None),
                        "amt": claim.get('amount', claim.get('amt', 0)),
                        "score": claim.get('score', 0),
                        "stars": claim.get('rating', claim.get('stars', None)),
                        "howKnown": claim.get('howKnown', 'WEB_DOCUMENT'),
                        "sourceURI": claim.get('sourceURI', claim.get('source', claims_data['filename'])),
                        "effectiveDate": claim.get('effectiveDate', datetime.now().isoformat()),
                        "confidence": claim.get('confidence', None),
                        "createdAt": claim.get('createdAt', datetime.now().isoformat()) 
                    }
                    
                    # Validate required fields
                    required_fields = ["subject", "claim", "object", "statement", "aspect", "howKnown", "sourceURI"]
                    missing_fields = [field for field in required_fields if not linkedtrust_payload.get(field)]
                    
                    if missing_fields:
                        failed_claims.append({
                            'claim': claim,
                            'error': f'Missing required fields: {", ".join(missing_fields)}'
                        })
                        continue
                    
                    # Post to LinkedTrust
                    result = auth_client.create_claim(linkedtrust_payload)
                    
                    if result["success"]:
                        # Extract claim ID from response
                        linkedtrust_claim_id = None
                        if isinstance(result["data"], dict):
                            if "claim" in result["data"]:
                                linkedtrust_claim_id = result["data"]["claim"].get("id")
                            else:
                                linkedtrust_claim_id = result["data"].get("id")
                        
                        # Update local claim status
                        claim['status'] = 'published'
                        claim['published_at'] = datetime.now().isoformat()
                        claim['linkedtrust_id'] = linkedtrust_claim_id
                        claim['linkedtrust_response'] = result["data"]
                        
                        published_claims.append({
                            'original_claim': claim,
                            'linkedtrust_id': linkedtrust_claim_id,
                            'linkedtrust_data': result["data"]
                        })
                        
                        logger.info(f"Successfully published claim to LinkedTrust with ID: {linkedtrust_claim_id}")
                        
                    else:
                        claim['status'] = 'failed'
                        claim['error'] = result["error"]
                        claim['failed_at'] = datetime.now().isoformat()
                        
                        failed_claims.append({
                            'claim': claim,
                            'error': result["error"],
                            'details': result.get("details", "")
                        })
                        
                        logger.error(f"Failed to publish claim: {result['error']}")
                        
                except Exception as e:
                    claim['status'] = 'failed'
                    claim['error'] = str(e)
                    claim['failed_at'] = datetime.now().isoformat()
                    
                    failed_claims.append({
                        'claim': claim,
                        'error': str(e)
                    })
                    
                    logger.error(f"Exception while publishing claim: {str(e)}")
        
        # Prepare response summary
        total_processed = len(published_claims) + len(failed_claims)
        success_rate = len(published_claims) / total_processed if total_processed > 0 else 0
        
        response_data = {
            'success': len(published_claims) > 0,
            'message': f'Processed {total_processed} claims. {len(published_claims)} published, {len(failed_claims)} failed.',
            'summary': {
                'total_processed': total_processed,
                'published_count': len(published_claims),
                'failed_count': len(failed_claims),
                'success_rate': round(success_rate * 100, 2)
            },
            'published_claims': published_claims,
            'failed_claims': failed_claims if failed_claims else None
        }
        
        status_code = 200 if len(published_claims) > 0 else 207  # 207 = Multi-Status
        
        return jsonify(response_data), status_code
        
    except Exception as e:
        logger.error(f"Error publishing claims to LinkedTrust: {str(e)}")
        return jsonify({
            'success': False, 
            'error': f'Failed to publish claims: {str(e)}'
        }), 500

@app.route('/api/claims/<claim_id>/publish/<int:claim_index>', methods=['POST'])
def publish_single_claim_to_linkedtrust(claim_id, claim_index):
    """API endpoint to publish a SINGLE claim to LinkedTrust"""
    if claim_id not in extracted_claims:
        return jsonify({'success': False, 'error': 'Claims not found'}), 404
    
    if not auth_client:
        return jsonify({'success': False, 'error': 'LinkedTrust not configured'}), 500
    
    try:
        claims_data = extracted_claims[claim_id]
        
        # Find the specific claim by index
        target_claim = None
        for claim in claims_data['claims']:
            if claim.get('claim_index') == claim_index:
                target_claim = claim
                break
        
        if not target_claim:
            return jsonify({'success': False, 'error': 'Specific claim not found'}), 404
        
        if target_claim.get('status') != 'draft':
            return jsonify({'success': False, 'error': f'Claim is already {target_claim.get("status")}'}), 400
        
        # Ensure we're authenticated with LinkedTrust
        if not auth_client.is_authenticated():
            auth_result = auth_client.auto_login()
            if not auth_result["success"]:
                return jsonify({
                    'success': False, 
                    'error': 'Failed to authenticate with LinkedTrust',
                    'details': auth_result["error"]
                }), 401
        
        try:
            # Transform the claim data to LinkedTrust format - FIXED null values
            linkedtrust_payload = {
                "subject": target_claim.get('subject') or 'Unknown Subject',
                "claim": target_claim.get('claim', target_claim.get('type', 'General Claim')),
                "object": target_claim.get('object', target_claim.get('description')) or 'Unknown Object',
                "statement": target_claim.get('statement', target_claim.get('description')) or 'No statement provided',
                "aspect": target_claim.get('aspect') or 'general',
                "amt": target_claim.get('amount', target_claim.get('amt', 0)),
                "score": target_claim.get('score', 0),
                "stars": target_claim.get('rating', target_claim.get('stars')) or 5,
                "howKnown": target_claim.get('howKnown', 'WEB_DOCUMENT'),
                "sourceURI": target_claim.get('sourceURI', target_claim.get('source', claims_data['filename'])),
                "effectiveDate": target_claim.get('effectiveDate', datetime.now().isoformat()),
                "confidence": target_claim.get('confidence') or 0.8
            }
            
            # Validate required fields
            required_fields = ["subject", "claim", "object", "statement", "aspect", "howKnown", "sourceURI"]
            missing_fields = [field for field in required_fields if not linkedtrust_payload.get(field)]
            
            if missing_fields:
                return jsonify({
                    'success': False,
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }), 400
            
            # Post to LinkedTrust
            result = auth_client.create_claim(linkedtrust_payload)
            
            if result["success"]:
                # Extract claim ID from response
                linkedtrust_claim_id = None
                if isinstance(result["data"], dict):
                    if "claim" in result["data"]:
                        linkedtrust_claim_id = result["data"]["claim"].get("id")
                    else:
                        linkedtrust_claim_id = result["data"].get("id")
                
                # Update local claim status
                target_claim['status'] = 'published'
                target_claim['published_at'] = datetime.now().isoformat()
                target_claim['linkedtrust_id'] = linkedtrust_claim_id
                target_claim['linkedtrust_response'] = result["data"]
                
                logger.info(f"Successfully published single claim to LinkedTrust with ID: {linkedtrust_claim_id}")
                
                return jsonify({
                    'success': True,
                    'message': f'Successfully published claim to LinkedTrust',
                    'linkedtrust_id': linkedtrust_claim_id,
                    'claim': target_claim
                }), 200
                
            else:
                target_claim['status'] = 'failed'
                target_claim['error'] = result["error"]
                target_claim['failed_at'] = datetime.now().isoformat()
                
                logger.error(f"Failed to publish single claim: {result['error']}")
                
                return jsonify({
                    'success': False,
                    'error': result["error"],
                    'details': result.get("details", "")
                }), 400
                
        except Exception as e:
            target_claim['status'] = 'failed'
            target_claim['error'] = str(e)
            target_claim['failed_at'] = datetime.now().isoformat()
            
            logger.error(f"Exception while publishing single claim: {str(e)}")
            
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
        
    except Exception as e:
        logger.error(f"Error publishing single claim to LinkedTrust: {str(e)}")
        return jsonify({
            'success': False, 
            'error': f'Failed to publish claim: {str(e)}'
        }), 500

@app.route('/api/config/status', methods=['GET'])
def config_status():
    """Check configuration status"""
    status = {
        'linkedtrust_configured': auth_client is not None,
        'claude_api_configured': claude_api_configured,
        'flask_secret_configured': bool(os.getenv('FLASK_SECRET_KEY')),
        'upload_folder_exists': os.path.exists(UPLOAD_FOLDER),
        'upload_folder_writable': os.access(UPLOAD_FOLDER, os.W_OK)
    }
    
    return jsonify({
        'status': status,
        'all_configured': all(status.values()),
        'configuration_details': {
            'linkedtrust_url': os.getenv('LINKEDTRUST_BASE_URL', 'https://dev.linkedtrust.us'),
            'claude_model': os.getenv('CLAUDE_MODEL', 'claude-3-sonnet-20240229'),
            'upload_folder': UPLOAD_FOLDER,
            'max_file_size': f"{MAX_CONTENT_LENGTH // (1024*1024)}MB"
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5050))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print("🚀 Starting Claim Extractor Web Application")
    print(f"📍 Server will run on http://localhost:{port}")
    print(f"🔐 LinkedTrust configured: {auth_client is not None}")
    print(f"🤖 Claude API configured: {claude_api_configured}")
    
    app.run(debug=debug, host="0.0.0.0", port=port)