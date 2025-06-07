# Testing Guide

## Method 1: Direct CLI Testing (Development)

🚀 **Step 1:** Try different phone number formats:  

**Option A - Test with US number (recommended first):**
```sh
lk dispatch create --new-room --agent-name ahoum-facilitator-onboarding --metadata '+15551234567'
```

**Option B - Indian number with country code:**
```sh
lk dispatch create --new-room --agent-name ahoum-facilitator-onboarding --metadata '+918767763794'
```

**Option C - Alternative Indian format:**
```sh
lk dispatch create --new-room --agent-name ahoum-facilitator-onboarding --metadata '00918767763794'
```

**Option D - Test with your own phone number:**
```sh
lk dispatch create --new-room --agent-name ahoum-facilitator-onboarding --metadata '+1YOURNUMBER'
```

🖥️ **Step 2:** In another terminal (with your virtual environment activated), run:  
```sh
python agent.py dev
```

## Method 2: API Testing (Production Ready)

### Setup
1. **Terminal 1 - Start the agent:**
```powershell
python agent.py dev
```

2. **Terminal 2 - Start the API server:**
```powershell
python api_server.py
```

### Test API Endpoints

**Test 1 - Health Check:**
```powershell
curl http://localhost:5000/health
```

**Test 2 - Single Call via API:**
```powershell
curl -X POST http://localhost:5000/call -H "Content-Type: application/json" -d '{"phone_number": "+918767763794"}'
```

**Test 3 - Batch Calls via API:**
```powershell
curl -X POST http://localhost:5000/call/batch -H "Content-Type: application/json" -d '{"phone_numbers": ["+918767763794", "+15551234567"]}'
```

**Test 4 - PowerShell Alternative:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/call" -Method POST -ContentType "application/json" -Body '{"phone_number": "+918767763794"}'
```

### Integration Example (Python)
```python
import requests

# Make a call
response = requests.post('http://localhost:5000/call', json={
    'phone_number': '+918767763794'
})

print(response.json())
```

📝 **Troubleshooting Notes:**
- New SIP Trunk ID: `ST_EZ63pCpQn3PT`
- For international calls, ensure your Twilio account has international permissions enabled
- Test with US numbers first as your Twilio number is US-based
- API runs on port 5000 by default
- Both agent and API server must be running simultaneously