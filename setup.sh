#!/bin/bash
set -e

echo "🔧 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed."
    echo "Please install Python 3 using Homebrew:"
    echo "brew install python"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Found Python $PYTHON_VERSION"

# Check if min version is met (3.7+)
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [[ "$PYTHON_MAJOR" -lt 3 || ("$PYTHON_MAJOR" -eq 3 && "$PYTHON_MINOR" -lt 7) ]]; then
    echo "❌ Python 3.7 or higher is required."
    echo "Please upgrade Python using Homebrew:"
    echo "brew upgrade python"
    exit 1
fi

echo "🔧 Setting up virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "🔧 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔧 Installing Intuit-specific dependencies..."
pip install openai langchain-openai --extra-index-url https://artifactory.a.intuit.com/artifactory/api/pypi/pypi-intuit/simple
pip install intlgntsys-mlplatform.coreaiauth.coreaiauth==2.1.0 --upgrade \
    --extra-index-url=https://artifact.intuit.com/artifactory/api/pypi/pypi-intuit/simple

echo "🔧 Setting up .env file..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "ℹ️ Created .env file. Please edit it with your credentials."
    echo "You'll need to provide CORP_ID and EMAIL values."
else
    echo "✅ .env file already exists."
fi

echo "🔧 Making run script executable..."
chmod +x run.sh

echo "✅ Setup complete!"
echo ""
echo "🚀 To run the script:"
echo "1. Edit .env file with your credentials (if you haven't already)"
echo "2. Run: ./run.sh"
echo ""
echo "The script will guide you through the SSO authentication process."
