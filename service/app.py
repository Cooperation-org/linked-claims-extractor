from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from pprint import pprint
from functools import wraps
from claim_extractor import ClaimExtractor

load_dotenv()

app = Flask(__name__)
CORS(app)

# Config
API_KEY = os.getenv('API_KEY')

PROMPT = """Here is a narrative about some work experience I had.  Please help me extract a list of skills and skill descriptions that an employer would recognize, that I could include in a resume. Try to find multiple skills, but ONLY list skills supported by the following work history:

"""

extractor = ClaimExtractor(schema_name='SIMPLE_SKILL')

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

if __name__ == '__main__':
    app.run(debug=True)
