# 🎫 Zoho Desk Call Ticket Processor

Automatically create Zoho Desk support tickets for Exotel calls with full transcriptions.

---

## ✨ Features

- ✅ **Auto-fetch calls** from Exotel API
- ✅ **Transcribe audio** using Deepgram
- ✅ **Analyze concern & mood** with OpenAI (or keyword fallback)
- ✅ **Create Zoho Desk tickets** automatically
- ✅ **Add transcription as private notes**
- ✅ **Auto-create/link contacts**
- ✅ **Token auto-refresh** for 24/7 operation

---

## 🚀 Quick Start

### **Step 1: Get Zoho Desk OAuth Credentials**

1. Go to [Zoho API Console](https://api-console.zoho.com/)
2. Click **"ADD CLIENT"** → Select **"Server-based Applications"**
3. Fill in:
   - **Client Name**: `Exotel Call Tickets`
   - **Homepage URL**: `http://localhost:8000`
   - **Authorized Redirect URIs**: `http://localhost:8000/oauth/callback`
4. Click **"CREATE"**
5. **Save your Client ID and Client Secret** ✅

### **Step 2: Generate Access Token**

1. In API Console, click your client → **"Generate Code"** tab
2. Select scopes:
   ```
   Desk.tickets.ALL
   Desk.contacts.ALL
   Desk.basic.READ
   ```
3. Set duration: 3-10 minutes
4. Click **"CREATE"** and copy the code

5. Exchange code for tokens (PowerShell):
   ```powershell
   $body = @{
       code = "YOUR_GENERATED_CODE"
       client_id = "YOUR_CLIENT_ID"
       client_secret = "YOUR_CLIENT_SECRET"
       redirect_uri = "http://localhost:8000/oauth/callback"
       grant_type = "authorization_code"
   }
   
   $response = Invoke-RestMethod -Uri "https://accounts.zoho.com/oauth/v2/token" -Method POST -Body $body
   $response | ConvertTo-Json
   ```

6. Save the **access_token** and **refresh_token** ✅

### **Step 3: Get Other Credentials**

1. **Organization ID**: Zoho Desk → Setup → Developer Space → API
2. **Department ID**: Setup → Departments → (check URL)
3. **Exotel credentials**: From your Exotel account
4. **Deepgram API key**: From [Deepgram Console](https://console.deepgram.com/)
5. **OpenAI API key** (optional): From [OpenAI Platform](https://platform.openai.com/)

### **Step 4: Configure**

1. Copy `env.example` to `.env`:
   ```bash
   copy env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```env
   EXOTEL_SID=abc6862
   EXOTEL_API_KEY=your_key
   EXOTEL_API_TOKEN=your_token
   
   DEEPGRAM_API_KEY=your_deepgram_key
   OPENAI_API_KEY=your_openai_key  # Optional
   
   ZOHO_DESK_ENABLED=true
   ZOHO_DESK_ORG_ID=60012345678
   ZOHO_DESK_ACCESS_TOKEN=1000.abc123...
   ZOHO_DESK_REFRESH_TOKEN=1000.xyz789...
   ZOHO_DESK_CLIENT_ID=1000.CLIENTID
   ZOHO_DESK_CLIENT_SECRET=your_client_secret
   ZOHO_DESK_DEPARTMENT_ID=123456789012345678
   ```

### **Step 5: Run**

```bash
start.bat
```

The processor will:
- Check for new calls every minute
- Download and transcribe recordings
- Create Zoho Desk tickets with transcriptions
- Auto-refresh tokens when expired

---

## 📋 What Gets Created

Each call creates a Zoho Desk ticket with:

### **Ticket Information:**
- **Subject**: `Call from {phone} - {concern}`
- **Description**: Call details, agent, time, duration, mood, concern
- **Channel**: Phone
- **Status**: Open
- **Priority**: Medium (configurable)

### **Private Note:**
- Full transcription text
- Call ID reference
- Marked as private (internal only)

### **Contact:**
- Auto-searches by phone number
- Auto-creates if not found
- Auto-links to ticket

---

## 📂 Project Structure

```
zoho-call-tickets/
├── zoho_call_processor.py     # Main processor
├── agents_config.json          # Agent configuration
├── requirements.txt            # Python dependencies
├── env.example                 # Environment template
├── start.bat                   # Windows startup script
├── README.md                   # This file
├── recordings/                 # Downloaded call recordings (auto-created)
├── processed_calls.json        # Tracking (auto-created)
└── zoho_processor.log          # Logs (auto-created)
```

---

## ⚙️ Configuration

### **Agent Configuration** (`agents_config.json`)

```json
{
  "agents": {
    "09631084471": {
      "name": "Prateek",
      "department": "Customer Success",
      "active": true
    }
  }
}
```

Add more agents as needed.

### **Environment Variables** (`.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `ZOHO_DESK_ENABLED` | Yes | Enable/disable integration |
| `ZOHO_DESK_ORG_ID` | Yes | Zoho organization ID |
| `ZOHO_DESK_ACCESS_TOKEN` | Yes | OAuth access token |
| `ZOHO_DESK_REFRESH_TOKEN` | Yes | OAuth refresh token |
| `ZOHO_DESK_CLIENT_ID` | Yes | OAuth client ID |
| `ZOHO_DESK_CLIENT_SECRET` | Yes | OAuth client secret |
| `ZOHO_DESK_DEPARTMENT_ID` | Yes | Department ID for tickets |
| `ZOHO_DESK_API_DOMAIN` | No | API domain (default: US) |
| `ZOHO_DESK_DEFAULT_PRIORITY` | No | Ticket priority (default: Medium) |
| `ZOHO_DESK_AUTO_CREATE_CONTACT` | No | Auto-create contacts (default: true) |

---

## 🔄 Token Auto-Refresh

The processor automatically refreshes access tokens when they expire (every 1 hour). It:
1. Detects 401 errors
2. Uses refresh token to get new access token
3. Updates `.env` file with new token
4. Retries the failed request

**No manual intervention needed!** ✅

---

## 🐛 Troubleshooting

### **"Zoho Desk credentials missing"**
- Check all required fields in `.env`
- Verify tokens are correct and not expired

### **"No agent detected for call"**
- Add agent phone number to `agents_config.json`
- Ensure number format matches Exotel format

### **"Transcription failed"**
- Verify Deepgram API key is valid
- Check internet connection
- Ensure recording downloaded successfully

### **"Token refresh failed"**
- Verify refresh token is correct
- Check client ID and secret
- Refresh token may have been revoked (regenerate)

### **"Failed to create ticket"**
- Verify department ID is correct
- Check organization ID
- Ensure Zoho account has permissions

---

## 📊 Monitoring

**Logs**: Check `zoho_processor.log` for detailed information

**Success indicators**:
```
✓ Created Zoho Desk ticket #12345 (ID: 123456789) for call abc123
✓ Added transcription note to ticket #12345
```

**Auto-refresh**:
```
Token expired, refreshing...
Successfully refreshed Zoho access token
```

---

## 🎯 Production Deployment

For 24/7 operation, deploy to:
- ✅ **Render** (free tier)
- ✅ **Railway** ($5 credit/month)
- ✅ **AWS EC2** (pay-as-you-go)
- ✅ **Fly.io** (free tier)

The processor includes token auto-refresh for unattended operation.

---

## 📖 Resources

- [Zoho Desk API Docs](https://www.zoho.com/desk/developer-guide/apiv1.html)
- [Zoho OAuth Guide](https://www.zoho.com/accounts/protocol/oauth/web-server-applications.html)
- [Deepgram API Docs](https://developers.deepgram.com/)
- [Exotel API Docs](https://developer.exotel.com/)

---

## ✅ Features Checklist

- [x] Fetch calls from Exotel
- [x] Download recordings
- [x] Transcribe with Deepgram
- [x] Analyze concern and mood
- [x] Create Zoho Desk tickets
- [x] Add transcription as notes
- [x] Auto-create/link contacts
- [x] Token auto-refresh
- [x] Duplicate prevention
- [x] Error handling
- [x] Logging

---

## 🎉 Ready to Use!

1. ✅ Configure `.env` with your credentials
2. ✅ Run `start.bat`
3. ✅ Watch tickets appear in Zoho Desk!

**No Slack, no webhooks, just pure Zoho Desk ticket creation.** 🚀

