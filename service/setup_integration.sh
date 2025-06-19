#!/bin/bash

# Setup script for linked-claims-extractor with backend integration

echo "Setting up Linked Claims Extractor with Backend Integration..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Create pending claims directory
mkdir -p pending_claims

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOL
# Extractor API Key (for legacy endpoints)
API_KEY=your-extractor-api-key

# Backend API URL
BACKEND_API_URL=http://localhost:3000

# LLM API Keys (at least one required)
ANTHROPIC_API_KEY=your-anthropic-key
# OPENAI_API_KEY=your-openai-key

# Optional: Default backend access token
# BACKEND_ACCESS_TOKEN=your-token
EOL
    echo "Please edit .env file with your actual API keys"
fi

echo ""
echo "Setup complete! 🎉"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Make sure trust-claim-backend is running on port 3000"
echo "3. Run the service with: python app.py"
echo "4. Test the integration with: python test_integration.py"
echo ""
echo "For more information, see INTEGRATION_README.md"
