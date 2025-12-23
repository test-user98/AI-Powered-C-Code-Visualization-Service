#!/bin/bash

echo "🚀 Setting up C Code Analyzer Frontend"
echo "====================================="

# Check if we're in the right directory
if [ ! -d "frontend" ]; then
    echo "❌ Error: frontend directory not found. Run this script from the project root."
    exit 1
fi

cd frontend

echo "📦 Installing dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
    echo ""
    echo "🎯 To start the frontend:"
    echo "   cd frontend"
    echo "   npm start"
    echo ""
    echo "🌐 Frontend will be available at: http://localhost:3000"
    echo "🔗 Make sure the backend is running at: http://localhost:8081"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
