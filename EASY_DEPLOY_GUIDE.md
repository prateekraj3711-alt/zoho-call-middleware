# 🚀 Super Easy Middleware Deployment Guide

## ✨ Don't Worry - This is REALLY Simple!

**No coding. No terminal. Just clicking buttons on websites.**

**Time: 15 minutes**

---

## 📋 What You Need (Preparation)

Before we start, have these ready:

1. ✅ **Exotel credentials** (from Exotel dashboard)
   - SID: `abc6862` (you have this)
   - API Key: `your_key`
   - API Token: `your_token`

2. ✅ **Deepgram API key** (free tier available)
   - Get from: https://console.deepgram.com/
   - Sign up → Copy API key

3. ✅ **OpenAI API key** (optional but recommended)
   - Get from: https://platform.openai.com/
   - Sign up → API Keys → Create new

4. ✅ **GitHub account** (free)
   - If you don't have one: https://github.com/signup

---

## 🎯 Three Steps to Deploy

1. **Push code to GitHub** (5 minutes)
2. **Deploy to Render** (5 minutes)
3. **Test it works** (5 minutes)

Let's go!

---

## 📦 Step 1: Push Code to GitHub (5 minutes)

### **Option A: Using GitHub Desktop** ⭐ Easiest

1. **Download GitHub Desktop**
   - Go to: https://desktop.github.com/
   - Download and install

2. **Open GitHub Desktop**
   - Sign in with your GitHub account

3. **Create new repository**
   - Click: **File → New Repository**
   - Name: `zoho-call-middleware`
   - Local Path: `G:\Projects\zoho-call-tickets`
   - Click: **Create Repository**

4. **Publish to GitHub**
   - Click: **Publish repository**
   - Uncheck "Keep this code private" (or keep checked, Render works with private repos)
   - Click: **Publish repository**

✅ **Done! Your code is on GitHub.**

### **Option B: Using Git Command Line**

If you prefer command line:

```bash
cd G:\Projects\zoho-call-tickets

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit"

# Create repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/zoho-call-middleware.git
git branch -M main
git push -u origin main
```

---

## ☁️ Step 2: Deploy to Render (5 minutes)

### **2.1: Create Render Account**

1. Go to: https://render.com/
2. Click: **Get Started**
3. Sign up with GitHub (easiest - one click)

### **2.2: Create New Web Service**

1. On Render dashboard, click: **New +**
2. Select: **Web Service**
3. Click: **Connect account** (if first time)
4. Find your repository: `zoho-call-middleware`
5. Click: **Connect**

### **2.3: Configure Service**

Fill in these fields:

| Field | Value |
|-------|-------|
| **Name** | `zoho-call-middleware` (or any name) |
| **Region** | Choose closest to you |
| **Branch** | `main` |
| **Root Directory** | Leave blank |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r middleware_requirements.txt` |
| **Start Command** | `gunicorn zapier_middleware:app` |
| **Instance Type** | **Free** ⭐ |

### **2.4: Add Environment Variables**

Scroll down to **Environment Variables** section.

Click: **Add Environment Variable**

Add these **one by one**:

| Key | Value (use YOUR credentials) |
|-----|------------------------------|
| `EXOTEL_SID` | `abc6862` |
| `EXOTEL_API_KEY` | Your Exotel API Key |
| `EXOTEL_API_TOKEN` | Your Exotel API Token |
| `DEEPGRAM_API_KEY` | Your Deepgram API Key |
| `OPENAI_API_KEY` | Your OpenAI API Key (optional) |

**Example:**
```
Key: EXOTEL_SID
Value: abc6862

Key: EXOTEL_API_KEY
Value: 4b28e36a0ada01074c969f7c51d7d36e08d638d4a4a46257

Key: EXOTEL_API_TOKEN
Value: ab79749a816e76055d06a4a4c6cc19218cfb6c06e81153a9

...and so on
```

### **2.5: Deploy!**

1. Click: **Create Web Service** (at the bottom)
2. Wait ~3-5 minutes (Render is building your app)
3. Watch the logs - you'll see:
   ```
   Building...
   Installing dependencies...
   Deploying...
   Live! ✅
   ```

### **2.6: Get Your Middleware URL**

Once deployed, you'll see:
```
Your service is live at https://zoho-call-middleware.onrender.com
```

**Copy this URL!** You'll need it for Zapier.

✅ **Middleware deployed!**

---

## ✅ Step 3: Test It Works (5 minutes)

### **3.1: Test Health Endpoint**

1. Open browser
2. Go to: `https://your-middleware.onrender.com/health`
3. You should see:
   ```json
   {
     "status": "healthy",
     "exotel_configured": true,
     "deepgram_configured": true,
     "openai_configured": true
   }
   ```

✅ **It's working!**

### **3.2: Test Process Call**

Use a tool like Postman or just use PowerShell:

```powershell
$response = Invoke-RestMethod -Uri "https://your-middleware.onrender.com/process_call" -Method POST
$response | ConvertTo-Json
```

You should see either:
- "no_new_calls" (if no new calls)
- Or actual call data with transcription!

✅ **Middleware is ready!**

---

## 🔧 Step 4: Set Up Zapier (10 minutes)

Now let's connect Zapier to your middleware.

### **4.1: Create New Zap**

1. Go to: https://zapier.com/
2. Click: **Create Zap**

### **4.2: Set Up Trigger**

1. **Trigger**: Schedule by Zapier
2. **Event**: Every X Minutes
3. **Interval**: 5 minutes
4. Click: **Continue**
5. Click: **Test trigger** (optional)

### **4.3: Call Your Middleware**

1. Click: **+ Add step**
2. Search: **Webhooks by Zapier**
3. **Event**: POST
4. Click: **Continue**

5. Configure:
   - **URL**: `https://your-middleware.onrender.com/process_call`
   - **Payload Type**: JSON
   - **Data**: Leave empty (or add `{}`)

6. Click: **Test step**

You should see response with call data or "no_new_calls"

### **4.4: Add Filter**

1. Click: **+ Add step**
2. Search: **Filter by Zapier**
3. **Condition**: Only continue if...
   - Field: `Status`
   - Condition: `(Text) Exactly matches`
   - Value: `success`
4. Click: **Continue**

### **4.5: Create Zoho Desk Ticket**

1. Click: **+ Add step**
2. Search: **Zoho Desk**
3. **Event**: Create Ticket
4. Click: **Sign in to Zoho Desk**
5. Authorize

6. Configure ticket:

| Field | Value |
|-------|-------|
| **Department** | Select your department |
| **Contact Phone** | `{{1. Customer Number}}` |
| **Subject** | `Call from {{1. Customer Number}} - {{1. Concern}}` |
| **Status** | Open |
| **Priority** | Medium |
| **Channel** | Phone |
| **Description** | Copy template below |

**Description Template:**
```
Call from {{1. Customer Number}}

📞 Call Details:
• Customer: {{1. Customer Number}}
• Agent: {{1. Agent Number}}
• Time: {{1. Call Time}}
• Duration: {{1. Duration}}
• Direction: {{1. Call Direction}}
• Mood: {{1. Mood}}

🎯 Concern Identified:
{{1. Concern}}

Call ID: {{1. Call Id}}

---
Auto-generated via Zapier
```

7. Click: **Continue**
8. Click: **Test step**

### **4.6: Add Transcription as Note**

1. Click: **+ Add step**
2. Search: **Zoho Desk**
3. **Event**: Add Comment to Ticket
4. Click: **Continue**

5. Configure:
   - **Ticket ID**: `{{2. Id}}` (from previous step)
   - **Content**: Copy template below
   - **Public**: No

**Content Template:**
```
📝 **Call Transcription**

{{1. Transcript}}

---
Call ID: {{1. Call Id}}
Transcription length: {{1. Transcription Length}} characters

*Auto-generated transcription from Exotel call recording*
```

6. Click: **Continue**
7. Click: **Test step**

### **4.7: Turn On Zap**

1. Name your Zap: **"Exotel → Zoho Desk (Transcription)"**
2. Click: **Publish**

✅ **Zap is live!**

---

## 🎉 You're Done!

**What happens now:**

Every 5 minutes:
1. ✅ Zapier triggers
2. ✅ Calls your middleware
3. ✅ Middleware checks Exotel for new calls
4. ✅ If new call found:
   - Downloads recording
   - Transcribes with Deepgram
   - Analyzes with OpenAI
   - Returns to Zapier
5. ✅ Zapier creates Zoho ticket
6. ✅ Zapier adds transcription as note

**All automatic!**

---

## 🐛 Troubleshooting

### **Middleware Issues**

**"Service build failed"**
→ Check the build logs on Render
→ Make sure all files are pushed to GitHub

**"Health check shows false"**
→ Check environment variables on Render
→ Make sure API keys are correct

**"Service keeps sleeping"**
→ Normal on free tier (wakes up in ~30 seconds when called)
→ Optional: Add UptimeRobot to keep it awake (see below)

### **Zapier Issues**

**"Webhook returned error"**
→ Check middleware logs on Render
→ Verify middleware URL is correct

**"No data in Zoho fields"**
→ Check Filter step - might be blocking
→ Verify middleware returned "status: success"

**"Transcription note not added"**
→ Verify Zoho Desk permissions
→ Check that ticket was created first

---

## 🚀 Optional: Keep Middleware Awake

Render free tier sleeps after 15 minutes of inactivity.

**Solution: Add a keep-alive ping**

### **Option 1: Use UptimeRobot (Free)**

1. Go to: https://uptimerobot.com/
2. Sign up (free)
3. Add New Monitor:
   - **Type**: HTTP(s)
   - **Friendly Name**: Zoho Middleware
   - **URL**: `https://your-middleware.onrender.com/health`
   - **Monitoring Interval**: 5 minutes
4. Click: **Create Monitor**

✅ **Middleware will stay awake!**

### **Option 2: Add to Zapier**

Create a second Zap:
1. **Trigger**: Schedule → Every 10 minutes
2. **Action**: Webhooks → GET → `https://your-middleware.onrender.com/health`

---

## 📊 What You Have Now

✅ **Middleware**: Running on Render (free, 24/7)  
✅ **Zapier**: Monitoring every 5 minutes  
✅ **Zoho Desk**: Auto-creating tickets  
✅ **Transcriptions**: In private notes  
✅ **AI Analysis**: Concern & mood  
✅ **Contacts**: Auto-linked  

**No recording URLs. Just transcriptions!** 🎉

---

## 💰 Costs

- **Render**: Free tier (sufficient)
- **Zapier**: Free for 100 tasks/month (20 calls)
- **Deepgram**: ~$0.01 per 2-minute call
- **OpenAI**: ~$0.001 per analysis

**Total: ~$1-2/month for 100 calls**

---

## 📞 Test It!

1. **Make a test call** on Exotel
2. **Wait 5 minutes**
3. **Check Zoho Desk** → You should see:
   - New ticket with call details
   - Private note with transcription

---

## ✅ Checklist

- [ ] Pushed code to GitHub
- [ ] Created Render account
- [ ] Deployed middleware to Render
- [ ] Added environment variables
- [ ] Tested `/health` endpoint
- [ ] Created Zapier workflow
- [ ] Connected Zoho Desk
- [ ] Tested complete flow
- [ ] Added keep-alive (optional)
- [ ] Made test call
- [ ] Verified ticket created with transcription

---

## 🎯 You Did It!

**Congratulations!** 🎉

You now have a fully automated system that:
- Monitors Exotel 24/7
- Transcribes every call
- Creates Zoho Desk tickets
- Adds transcriptions as notes

**All running in the cloud, automatically!**

---

## ❓ Need Help?

**Render logs:** https://dashboard.render.com/ → Your service → Logs  
**Zapier history:** https://zapier.com/ → Zap History  
**Test endpoint:** `https://your-middleware.onrender.com/health`

**Common issue: "Service sleeping"**
→ Normal on free tier. First request wakes it up (~30 seconds)
→ Use UptimeRobot to keep it awake

---

**You're all set! 🚀**

