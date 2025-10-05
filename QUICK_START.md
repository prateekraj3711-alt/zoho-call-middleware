# 🚀 Quick Start Guide

## 3-Step Setup

### **1. Create Zoho OAuth Client**

✅ You're already on this page: https://api-console.zoho.com/#/web

**Fill in the form:**
- **Client Name**: `Exotel Call Tickets`
- **Homepage URL**: `http://localhost:8000`
- **Authorized Redirect URIs**: `http://localhost:8000/oauth/callback`

Click **"CREATE"** → Save your **Client ID** and **Client Secret**

---

### **2. Generate Tokens**

After creating the client:

1. Click your client name → **"Generate Code"** tab
2. Select scopes:
   - `Desk.tickets.ALL`
   - `Desk.contacts.ALL`
   - `Desk.basic.READ`
3. Set duration: **10 minutes**
4. Click **"CREATE"** → Copy the code

5. Run in PowerShell:
```powershell
$body = @{
    code = "PASTE_YOUR_CODE_HERE"
    client_id = "YOUR_CLIENT_ID"
    client_secret = "YOUR_CLIENT_SECRET"
    redirect_uri = "http://localhost:8000/oauth/callback"
    grant_type = "authorization_code"
}

$response = Invoke-RestMethod -Uri "https://accounts.zoho.com/oauth/v2/token" -Method POST -Body $body
$response | ConvertTo-Json
```

6. Copy the **access_token** and **refresh_token** from the response

---

### **3. Configure & Run**

```bash
# 1. Navigate to project
cd G:\Projects\zoho-call-tickets

# 2. Run setup script
python setup.py

# 3. Enter your credentials when prompted

# 4. Start the processor
start.bat
```

---

## 📋 Credentials You Need

| Credential | Where to Get It |
|------------|-----------------|
| **Exotel SID** | Exotel Dashboard |
| **Exotel API Key** | Exotel → Settings → API |
| **Exotel API Token** | Exotel → Settings → API |
| **Deepgram API Key** | [console.deepgram.com](https://console.deepgram.com/) |
| **OpenAI API Key** | [platform.openai.com](https://platform.openai.com/) (optional) |
| **Zoho Org ID** | Zoho Desk → Setup → Developer Space → API |
| **Zoho Department ID** | Setup → Departments (check URL) |
| **Zoho Access Token** | From step 2 above |
| **Zoho Refresh Token** | From step 2 above |
| **Zoho Client ID** | From step 1 above |
| **Zoho Client Secret** | From step 1 above |

---

## ✅ Quick Checklist

- [ ] Created Zoho OAuth client
- [ ] Generated access & refresh tokens
- [ ] Got Exotel credentials
- [ ] Got Deepgram API key
- [ ] Got Zoho Org ID & Department ID
- [ ] Ran `python setup.py`
- [ ] Updated `agents_config.json` with agent numbers
- [ ] Ran `start.bat`
- [ ] Checked `zoho_processor.log` for activity

---

## 🎯 What Happens Next

Once running, the processor will:
1. ✅ Check Exotel for new calls every minute
2. ✅ Download call recordings
3. ✅ Transcribe using Deepgram
4. ✅ Analyze concern & mood
5. ✅ Create Zoho Desk tickets
6. ✅ Add transcription as private notes
7. ✅ Auto-refresh tokens when expired

---

## 🐛 Common Issues

**"Missing credentials"**
→ Run `python setup.py` again

**"Token expired"**
→ Will auto-refresh automatically (check if refresh token is set)

**"No agent detected"**
→ Add agent number to `agents_config.json`

**"Failed to create ticket"**
→ Verify department ID and organization ID

---

## 📖 Full Documentation

See `README.md` for complete documentation.

---

## ✨ You're Done!

Tickets will now automatically appear in Zoho Desk for every new call! 🎉

