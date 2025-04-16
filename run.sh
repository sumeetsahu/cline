#!/bin/bash
set -e

# Activate virtual environment
source .venv/bin/activate

# Run the token generation script with any passed arguments
python TokenGeneration_env.py "$@"

echo ""
echo "✅ Script execution completed."
echo "If authentication was successful, you can now use the generated headers for your API calls."
