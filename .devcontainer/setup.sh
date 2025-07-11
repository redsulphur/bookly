#!/bin/bash

# Configure Git to work properly in the container
git config --global --add safe.directory /workspace
git config --global init.defaultBranch main

# Set up Git if user info is not configured
if [ -z "$(git config --global user.name)" ]; then
    echo "Setting up Git user configuration..."
    git config --global user.name "Dev Container User"
    git config --global user.email "dev@example.com"
fi

# Install Python dependencies
pip install -r app/requirements.txt

echo "Container setup complete!"
