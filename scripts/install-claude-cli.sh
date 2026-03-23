#!/bin/bash
# Install Claude Code CLI on Linux (Ubuntu/Debian)
set -e

echo "Installing Claude Code CLI..."

# Install curl if not present
if ! command -v curl &>/dev/null; then
    echo "curl not found. Installing curl..."
    sudo apt update && sudo apt install -y curl
fi

# Install Claude Code
curl -fsSL https://claude.ai/install.sh | bash

echo ""
echo "Claude Code installed successfully!"
echo "Run 'claude --version' to verify."
echo "Run 'claude' to start."
