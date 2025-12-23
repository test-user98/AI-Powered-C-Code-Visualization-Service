#!/bin/bash
# Test script for API endpoints

echo "🧪 Testing C Code Analyzer API"
echo "================================"

# Test health check
echo "1️⃣ Testing health check..."
if curl -s http://localhost:8080/ > /dev/null; then
    echo "✅ API is responding!"
    curl -s http://localhost:8080/
else
    echo "❌ API not responding. Start server with: python app/main.py"
    exit 1
fi

echo ""
echo "2️⃣ Testing jobs endpoint..."
curl -s http://localhost:8080/api/jobs | jq . 2>/dev/null || curl -s http://localhost:8080/api/jobs

echo ""
echo "3️⃣ Creating a test job..."
JOB_RESPONSE=$(curl -s -X POST http://localhost:8080/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "code": "#include <stdio.h>\n\nint factorial(int n) {\n    if (n <= 1) return 1;\n    return n * factorial(n - 1);\n}\n\nint main(void) {\n    printf(\"%d\\n\", factorial(5));\n    return 0;\n}"
  }')

echo "Job creation response:"
echo "$JOB_RESPONSE" | jq . 2>/dev/null || echo "$JOB_RESPONSE"

# Extract job ID if available
JOB_ID=$(echo "$JOB_RESPONSE" | jq -r '.job_id' 2>/dev/null || echo "")
if [ -n "$JOB_ID" ] && [ "$JOB_ID" != "null" ]; then
    echo ""
    echo "4️⃣ Monitoring job progress..."
    echo "💡 Job ID: $JOB_ID"
    echo "💡 Run WebSocket test in another terminal: python test_websocket.py"
    echo ""
    echo "Manual job status check:"
    echo "curl http://localhost:8080/api/jobs/$JOB_ID"
fi

echo ""
echo "🎯 Test complete!"
echo "💡 For real-time updates, run: python test_websocket.py"
