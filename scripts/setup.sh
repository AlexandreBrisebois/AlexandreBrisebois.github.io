#!/bin/bash
# srvrlss.dev - Zero Friction Setup Script

echo "🚀 Initializing srvrlss.dev development environment..."

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js (>=22.12.0)."
    exit 1
fi

NODE_VERSION=$(node -v | cut -d 'v' -f 2)
echo "Found Node.js v$NODE_VERSION"

# Install dependencies with legacy peer deps for Astro 6 stability
echo "📦 Installing dependencies..."
npm install --legacy-peer-deps

echo "✅ Setup complete. Run 'npm run dev' to start local development."
