#!/bin/bash

# Script to package Cline VS Code extension

# Exit immediately if a command exits with a non-zero status
set -e

echo "===== Cline VS Code Extension Packaging Script ====="

# Check if vsce is installed
if ! command -v vsce &> /dev/null; then
    echo "Installing vsce globally..."
    npm install -g vsce
fi

# Determine the extension directory (either current directory or specified path)
EXTENSION_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Packaging extension from: $EXTENSION_DIR"

# Navigate to extension directory
cd "$EXTENSION_DIR"

# Install dependencies
echo "Installing dependencies..."
npm install

# Build the project
echo "Building the project..."
npm run package

# Create VSIX package
echo "Creating VSIX package..."
vsce package

# Find the generated VSIX file
VSIX_FILE=$(find . -maxdepth 1 -name "*.vsix" -type f -printf "%T@ %p\n" | sort -n | tail -1 | cut -d' ' -f2-)

if [ -n "$VSIX_FILE" ]; then
    VSIX_PATH="$EXTENSION_DIR/$(basename "$VSIX_FILE")"
    echo "===== Packaging Complete ====="
    echo "VSIX file created at: $VSIX_PATH"
    echo ""
    echo "To install the extension, use one of these methods:"
    echo "1. VS Code UI: Extensions view → ... menu → \"Install from VSIX\""
    echo "2. Command Palette: \"Extensions: Install from VSIX\""
    echo "3. Command Line: code --install-extension \"$VSIX_PATH\""
else
    echo "===== Error ====="
    echo "Failed to find the generated VSIX file."
    exit 1
fi
