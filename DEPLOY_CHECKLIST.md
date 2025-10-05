# ✅ Quick Deploy Checklist

## 🎯 Goal: Get Transcriptions in Zoho Desk Tickets

---

## 📋 Before You Start

Gather these credentials:

- [ ] **Exotel SID**: `abc6862` ✅
- [ ] **Exotel API Key**: _____________
- [ ] **Exotel API Token**: _____________
- [ ] **Deepgram API Key**: _____________ (get from console.deepgram.com)
- [ ] **OpenAI API Key**: _____________ (optional, get from platform.openai.com)

---

## 🚀 Deployment (15 minutes)

### **Step 1: GitHub** (5 min)

- [ ] Download GitHub Desktop: https://desktop.github.com/
- [ ] Sign in to GitHub
- [ ] File → New Repository
  - Name: `zoho-call-middleware`
  - Path: `G:\Projects\zoho-call-tickets`
- [ ] Click: Publish repository
- [ ] ✅ **Code is on GitHub!**

---

### **Step 2: Render** (5 min)

- [ ] Go to: https://render.com/
- [ ] Sign up with GitHub
- [ ] Click: New + → Web Service
- [ ] Connect: `zoho-call-middleware` repo
- [ ] Configure:
  - Name: `zoho-call-middleware`
  - Runtime: `Python 3`
  - Build: `pip install -r middleware_requirements.txt`
  - Start: `gunicorn zapier_middleware:app`
  - Instance: **Free**
- [ ] Add Environment Variables:
  - `EXOTEL_SID` = your_sid
  - `EXOTEL_API_KEY` = your_key
  - `EXOTEL_API_TOKEN` = your_token
  - `DEEPGRAM_API_KEY` = your_key
  - `OPENAI_API_KEY` = your_key (optional)
- [ ] Click: Create Web Service
- [ ] Wait 5 minutes for deployment
- [ ] Copy URL: `https://zoho-call-middleware.onrender.com`
- [ ] Test: Open `https://your-url.onrender.com/health` in browser
- [ ] ✅ **Middleware is live!**

---

### **Step 3: Zapier** (10 min)

- [ ] Go to: https://zapier.com/
- [ ] Create Zap

**Trigger:**
- [ ] Schedule by Zapier → Every 5 minutes

**Action 1: Call Middleware**
- [ ] Webhooks by Zapier → POST
- [ ] URL: `https://your-middleware.onrender.com/process_call`

**Action 2: Filter**
- [ ] Filter by Zapier
- [ ] Only if: `Status` exactly matches `success`

**Action 3: Create Ticket**
- [ ] Zoho Desk → Create Ticket
- [ ] Sign in to Zoho Desk
- [ ] Configure:
  - Department: Your dept
  - Contact Phone: `{{Customer Number}}`
  - Subject: `Call from {{Customer Number}} - {{Concern}}`
  - Description: (use template from guide)

**Action 4: Add Note**
- [ ] Zoho Desk → Add Comment
- [ ] Ticket ID: `{{Id}}` from previous step
- [ ] Content: `{{Transcript}}`
- [ ] Public: No

**Finish:**
- [ ] Name: "Exotel → Zoho Desk"
- [ ] Click: Publish
- [ ] ✅ **Zap is live!**

---

## 🧪 Test (5 min)

- [ ] Make test call on Exotel
- [ ] Wait 5 minutes
- [ ] Check Zoho Desk
- [ ] Verify:
  - [ ] Ticket created
  - [ ] Has call details
  - [ ] Has transcription in notes
- [ ] ✅ **IT WORKS!**

---

## 🎉 You're Done!

**What you have:**
- ✅ Middleware running on Render (free, 24/7)
- ✅ Zapier checking every 5 minutes
- ✅ Auto-transcription with Deepgram
- ✅ AI analysis with OpenAI
- ✅ Tickets in Zoho Desk with transcriptions

---

## 📖 Full Guides

- **EASY_DEPLOY_GUIDE.md** - Step-by-step with details
- **ZAPIER_WITH_TRANSCRIPTION.md** - Complete workflow guide
- **ZAPIER_NO_MIDDLEWARE.md** - Why middleware is needed

---

## 🐛 Troubleshooting

**Middleware not responding?**
→ Free tier sleeps after 15min. First request wakes it (~30s)

**No tickets created?**
→ Check Zapier history, verify filter not blocking

**No transcription in notes?**
→ Check Zoho Desk permissions for adding comments

**Need help?**
→ Open EASY_DEPLOY_GUIDE.md for detailed instructions

---

## ⏱️ Total Time: ~30 minutes

**Then automatic forever!** 🚀

