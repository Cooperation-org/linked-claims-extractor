#!/bin/bash
set -e  # Exit on any error

# Check if direnv is installed
if ! command -v direnv &> /dev/null; then
    echo "direnv not found. Installing..."
    if command -v brew &> /dev/null; then
        brew install direnv
    elif command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y direnv
    else
        echo "Please install direnv manually: https://direnv.net/docs/installation.html"
        exit 1
    fi
fi

# Detect shell and add hook if not present
CURRENT_SHELL=$(basename "$SHELL")
SHELL_CONFIG=""

case "$CURRENT_SHELL" in
    "bash")
        SHELL_CONFIG="$HOME/.bashrc"
        ;;
    "zsh")
        SHELL_CONFIG="$HOME/.zshrc"
        ;;
    *)
        SHELL_CONFIG=""
        ;;
esac

if [ -n "$SHELL_CONFIG" ]; then
    if ! grep -q "eval \"\$(direnv hook $CURRENT_SHELL)\"" "$SHELL_CONFIG"; then
        echo "eval \"\$(direnv hook $CURRENT_SHELL)\"" >> "$SHELL_CONFIG"
        echo "Added direnv hook to $SHELL_CONFIG"
    fi
fi


# Function to setup a project directory
setup_project() {
    local project_dir="$1"
    echo "Setting up $project_dir..."
    
    cd "$project_dir"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        echo "Created virtual environment in $project_dir/.venv"
    fi
    
    # Create or update .envrc
    echo 'source .venv/bin/activate' > .envrc
    direnv allow
    
    # Install requirements and package
    if [ -f "requirements.txt" ]; then
        .venv/bin/pip install -r requirements.txt
    fi
    
    if [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
        .venv/bin/pip install -e .
    fi
    
    cd ..
    echo "Completed setup for $project_dir"
    echo "----------------------------------------"
}

# Main script
echo "Starting local development setup..."

# Find all directories that might be Python projects
for dir in */; do
    if [ -f "${dir}requirements.txt" ] || [ -f "${dir}setup.py" ] || [ -f "${dir}pyproject.toml" ]; then
        setup_project "${dir%/}"  # Remove trailing slash
    fi
done

# At the end of the script:
echo "----------------------------------------"
if [ -z "$SHELL_CONFIG" ]; then
    echo "Please add the appropriate direnv hook to your shell's config file:"
    echo ""
    echo "For bash: Add to ~/.bashrc:"
    echo 'eval "$(direnv hook bash)"'
    echo ""
    echo "For zsh: Add to ~/.zshrc:"
    echo 'eval "$(direnv hook zsh)"'
    echo ""
    echo "For fish: Add to ~/.config/fish/config.fish:"
    echo 'direnv hook fish | source'
    echo ""
else
    echo "Setup complete! Please restart your shell or run:"
    echo "source $SHELL_CONFIG"
fi
