#!/bin/bash

echo "Installing Node.js 18 LTS for Quiz Master frontend..."
echo "================================================="

# Remove existing Node.js
sudo apt remove -y nodejs npm

# Install Node.js 18 LTS using NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

echo "Node.js installation completed!"
echo "Node.js version: $(node --version)"
echo "npm version: $(npm --version)"

echo ""
echo "Now you can run the Quiz Master application:"
echo "1. Backend is already running on http://localhost:5000"
echo "2. To start frontend: cd frontend && npm install && npm run dev"
