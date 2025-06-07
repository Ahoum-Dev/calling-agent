# Production Deployment Guide

## Overview
This guide shows how to deploy the Ahoum Facilitator Onboarding Agent in production with API endpoints.

## Architecture
```
┌─────────────────┐    HTTP POST     ┌─────────────────┐    lk dispatch    ┌─────────────────┐
│   Your App/     │ ─────────────►   │   API Server    │ ─────────────►    │  LiveKit Agent  │
│   Frontend      │                  │  (api_server.py)│                   │   (agent.py)    │
└─────────────────┘                  └─────────────────┘                   └─────────────────┘
                                              │                                       │
                                              ▼                                       ▼
                                     ┌─────────────────┐                   ┌─────────────────┐
                                     │  LiveKit CLI    │                   │   Phone Call    │
                                     │   Commands      │                   │   via Twilio    │
                                     └─────────────────┘                   └─────────────────┘
```

## Deployment Steps

### Step 1: Install Additional Dependencies
```powershell
pip install flask flask-cors
```

### Step 2: Run the Agent (Terminal 1)
```powershell
python agent.py dev
```
Keep this running - it handles the actual phone calls.

### Step 3: Run the API Server (Terminal 2)
```powershell
python api_server.py
```
This starts the HTTP API on port 5000.

## API Endpoints

### 1. Health Check
```http
GET http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Ahoum Facilitator Onboarding API"
}
```

### 2. Make Single Call
```http
POST http://localhost:5000/call
Content-Type: application/json

{
  "phone_number": "+918767763794"
}
```

**Success Response:**
```json
{
  "success": true,
  "message": "Call initiated successfully to +918767763794",
  "phone_number": "+918767763794",
  "dispatch_info": "Dispatch created: id:\"AD_xyz123\" ..."
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Invalid phone number format. Use international format like +918767763794"
}
```

### 3. Make Batch Calls
```http
POST http://localhost:5000/call/batch
Content-Type: application/json

{
  "phone_numbers": [
    "+918767763794",
    "+919876543210", 
    "+15551234567"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Processed 3 calls, 2 successful",
  "results": [
    {
      "phone_number": "+918767763794",
      "success": true,
      "dispatch_info": "Dispatch created: ..."
    },
    {
      "phone_number": "+919876543210",
      "success": false,
      "error": "SIP error 480"
    }
  ]
}
```

## Integration Examples

### Python Example
```python
import requests

# Single call
response = requests.post('http://localhost:5000/call', json={
    'phone_number': '+918767763794'
})

if response.json()['success']:
    print("Call initiated successfully!")
else:
    print(f"Error: {response.json()['error']}")

# Batch calls
response = requests.post('http://localhost:5000/call/batch', json={
    'phone_numbers': ['+918767763794', '+919876543210']
})

print(f"Results: {response.json()}")
```

### JavaScript/Node.js Example
```javascript
// Single call
const response = await fetch('http://localhost:5000/call', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    phone_number: '+918767763794'
  })
});

const result = await response.json();
console.log(result);
```

### cURL Example
```bash
# Single call
curl -X POST http://localhost:5000/call \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+918767763794"}'

# Batch calls
curl -X POST http://localhost:5000/call/batch \
  -H "Content-Type: application/json" \
  -d '{"phone_numbers": ["+918767763794", "+919876543210"]}'
```

## Production Deployment Options

### Option 1: Simple Server Deployment
1. Deploy both `agent.py` and `api_server.py` on the same server
2. Use a process manager like PM2 or systemd to keep them running
3. Use nginx as a reverse proxy

### Option 2: Container Deployment
```dockerfile
# Dockerfile example
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# You'll need to run both processes
CMD ["python", "api_server.py"]
```

### Option 3: Cloud Functions (Advanced)
- Deploy API server as a cloud function
- Keep the agent running on a dedicated server

## Environment Variables

Add to your `.env.local`:
```env
# API Configuration
API_PORT=5000
DEBUG=false

# Existing LiveKit/Twilio config
LIVEKIT_URL=...
LIVEKIT_API_KEY=...
# ... other existing vars
```

## Security Considerations

1. **Authentication**: Add API key authentication for production
2. **Rate Limiting**: Implement rate limiting to prevent abuse
3. **Input Validation**: Phone number validation is included
4. **HTTPS**: Use HTTPS in production
5. **Firewall**: Restrict API access to known IPs

## Monitoring

The API includes logging. Monitor:
- Call success rates
- Response times
- Error patterns
- Phone number validation failures

## Testing

Test the deployment:
```powershell
# Terminal 1: Start agent
python agent.py dev

# Terminal 2: Start API
python api_server.py

# Terminal 3: Test API
curl -X POST http://localhost:5000/call -H "Content-Type: application/json" -d '{"phone_number": "+15551234567"}'
```
