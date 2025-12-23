# 🧪 Testing Guide: WebSocket Real-Time Updates

## Overview
This guide shows how to test the WebSocket real-time update functionality of the C Code Analyzer.

## Prerequisites
- Python 3.11+ with dependencies installed
- Backend server running
- WebSocket test client (optional)

## 🚀 Quick Start Testing

### 1. Start the Backend Server
```bash
cd /Users/test/c_code_analyzer_backend
python app/main.py
```
**Expected output:**
```
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

### 2. Test API Endpoints
```bash
# Test health check
curl http://localhost:8080/

# Test jobs listing
curl http://localhost:8080/api/jobs
```

**Expected response:**
```json
{"message": "C Code Analyzer API", "status": "running"}
```

### 3. Test WebSocket Connection
```bash
# Run the WebSocket test (requires websockets library)
pip install websockets aiohttp
python test_websocket.py
```

**Expected output:**
```
🧪 Testing WebSocket Real-Time Updates
==================================================

1️⃣ Testing API endpoints...
✅ API health check passed!
   Response: {'message': 'C Code Analyzer API', 'status': 'running'}
✅ Jobs API working!
   Jobs count: 0

2️⃣ Testing WebSocket connection...
✅ WebSocket connected successfully!
📡 Listening for real-time job updates...
```

### 4. Create a Test Job (Terminal 2)
While WebSocket test is running, create a job in another terminal:

```bash
curl -X POST http://localhost:8080/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "code": "#include <stdio.h>\n\nint factorial(int n) {\n    if (n <= 1) return 1;\n    return n * factorial(n - 1);\n}\n\nint main(void) {\n    printf(\"%d\\n\", factorial(5));\n    return 0;\n}"
  }'
```

### 5. Watch Real-Time Updates
In the WebSocket test terminal, you should see:
```
📨 Received update: {
  "type": "job_update",
  "job_id": "uuid-here",
  "status": "in_progress",
  "total_functions": 2,
  "processed_functions": 0,
  "updated_at": "2025-12-23T09:18:45.123456"
}
📨 Received update: {
  "type": "job_update",
  "job_id": "uuid-here",
  "status": "in_progress",
  "total_functions": 2,
  "processed_functions": 1,
  "updated_at": "2025-12-23T09:18:46.234567"
}
📨 Received update: {
  "type": "job_update",
  "job_id": "uuid-here",
  "status": "success",
  "total_functions": 2,
  "processed_functions": 2,
  "updated_at": "2025-12-23T09:18:47.345678"
}
```

## 🖥️ Frontend Testing

### 1. Start Frontend Development Server
```bash
cd frontend
npm install
npm start
```
**Expected:** Frontend opens at `http://localhost:3000`

### 2. Test Real-Time Updates in Browser
1. Open browser console (F12 → Console)
2. Submit C code using the form
3. Watch console for WebSocket messages:
```
WebSocket connected for job updates
```
4. Watch job progress update instantly as functions are processed

## 🧪 Manual Testing Commands

### Test API with Bash Script
```bash
# Make script executable
chmod +x test_api.sh

# Run tests
./test_api.sh
```

### Manual WebSocket Testing
```bash
# Using websocat (if installed)
echo "Test" | websocat ws://localhost:8080/ws/jobs

# Using Node.js
node -e "
const WebSocket = require('ws');
const ws = new WebSocket('ws://localhost:8080/ws/jobs');
ws.on('open', () => console.log('Connected'));
ws.on('message', (data) => console.log('Received:', data.toString()));
"
```

## 🔍 Troubleshooting

### Backend Won't Start
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution:**
```bash
pip install -r requirements.txt
```

### WebSocket Connection Fails
```
ConnectionRefusedError
```
**Solution:** Ensure backend is running on port 8080

### No Real-Time Updates
- Check WebSocket connection in browser dev tools
- Verify job creation is successful
- Check backend logs for WebSocket messages

### Frontend Issues
- Clear browser cache
- Check console for WebSocket errors
- Verify API_URL in frontend matches backend port

## 📊 Expected Test Results

### ✅ Successful Test Indicators
- ✅ Backend starts without errors
- ✅ API endpoints return 200 status
- ✅ WebSocket connects successfully
- ✅ Job creation returns valid job_id
- ✅ Real-time updates appear in WebSocket client
- ✅ Frontend shows instant progress updates
- ✅ Job completes with success status

### ❌ Common Issues & Solutions

| Issue | Symptom | Solution |
|-------|---------|----------|
| Import Error | `ModuleNotFoundError` | `pip install -r requirements.txt` |
| Port Conflict | `Address already in use` | Change port in `app/main.py` |
| WebSocket Fail | `Connection refused` | Check backend is running |
| No Updates | WebSocket connects but no messages | Check job processing logic |
| CORS Error | Frontend can't connect | Verify CORS settings |

## 🎯 Performance Testing

### Load Testing WebSocket
```bash
# Test multiple concurrent connections
for i in {1..10}; do
  python test_websocket.py &
done

# Monitor server performance
htop  # or activity monitor
```

### Memory & CPU Monitoring
```bash
# Monitor backend process
ps aux | grep python

# Check WebSocket connection count (in backend logs)
tail -f /dev/null  # Run backend with logging
```

## 📝 Test Checklist

- [ ] Backend server starts successfully
- [ ] API health check returns 200
- [ ] WebSocket endpoint accepts connections
- [ ] Job creation works via API
- [ ] Real-time updates are broadcast
- [ ] Frontend connects via WebSocket
- [ ] Progress updates appear instantly
- [ ] Job completion triggers final update
- [ ] Multiple clients receive updates
- [ ] Connection handles disconnect/reconnect

## 🚀 Next Steps

Once testing is complete:
1. **Deploy to production** with Docker
2. **Monitor WebSocket performance**
3. **Add authentication** if needed
4. **Scale horizontally** for multiple servers

## 📞 Support

If tests fail, check:
- Backend logs for errors
- Browser console for WebSocket issues
- Network connectivity
- Port availability

**Happy testing! 🧪✨**
