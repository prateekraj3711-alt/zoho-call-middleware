# 🔄 Zapier → Zoho Desk Solution

## ✨ Overview

Instead of running a local processor, use **Zapier** to automatically create Zoho Desk tickets when new calls come from Exotel.

---

## 🎯 Workflow

```
Exotel Call → Zapier Webhook → Process → Zoho Desk Ticket
```

**No servers needed!** Everything runs in Zapier's cloud.

---

## 🧩 Setup Steps

### **Step 1: Create Zoho Desk Connection in Zapier**

1. Go to [Zapier](https://zapier.com/)
2. Create new Zap
3. Add **Zoho Desk** as an action
4. When prompted, authorize Zapier to access Zoho Desk
5. Select your organization and department

✅ **Done!** Zapier now has access to create tickets.

---

### **Step 2: Create Exotel → Zapier Webhook**

#### **Option A: Using Exotel Webhooks (Best)**

If Exotel supports webhooks:

1. In Zapier, create new Zap
2. **Trigger**: Webhooks by Zapier → Catch Hook
3. Copy the webhook URL
4. In Exotel settings, add webhook for "Call Completed" events
5. Test by making a call

#### **Option B: Using Code by Zapier (Polling)**

If no webhooks available:

1. **Trigger**: Schedule by Zapier → Every 5 minutes
2. **Action**: Code by Zapier → Python
3. Fetch calls from Exotel API
4. Return call data

---

### **Step 3: Set Up Complete Zapier Workflow**

Here's the complete Zap structure:

```
1. TRIGGER
   ├─ Webhooks by Zapier: Catch Hook
   └─ OR Schedule: Every 5 minutes

2. (Optional) Code by Zapier: Fetch Exotel Calls
   └─ Download recording & transcribe

3. (Optional) Code by Zapier: Analyze with OpenAI
   └─ Get concern and mood

4. ACTION: Zoho Desk → Create Ticket
   ├─ Subject: Call from {{phone}}
   ├─ Description: {{details}}
   └─ Priority: Medium

5. ACTION: Zoho Desk → Add Comment (Note)
   └─ Content: {{transcription}}
```

---

## 📝 Zapier Code Examples

### **Code 1: Fetch Exotel Calls (Python)**

```python
import requests
from datetime import datetime, timedelta

# Exotel credentials from Zapier Storage
exotel_sid = "YOUR_EXOTEL_SID"
exotel_key = "YOUR_EXOTEL_KEY"
exotel_token = "YOUR_EXOTEL_TOKEN"

# Fetch calls from last 10 minutes
url = f"https://api.exotel.com/v1/Accounts/{exotel_sid}/Calls.json"
auth = (exotel_key, exotel_token)
params = {"PageSize": 10, "Page": 0}

response = requests.get(url, auth=auth, params=params)
if response.status_code == 200:
    calls = response.json().get("Calls", [])
    
    # Get first completed call with recording
    for call in calls:
        if call.get("Status") == "completed" and call.get("RecordingUrl"):
            output = {
                "call_id": call.get("Sid"),
                "from_number": call.get("From", {}).get("PhoneNumber"),
                "to_number": call.get("To", {}).get("PhoneNumber"),
                "duration": call.get("Duration"),
                "recording_url": call.get("RecordingUrl"),
                "call_time": call.get("DateCreated")
            }
            break
else:
    output = {"error": "Failed to fetch calls"}

# Return for next step
return output
```

### **Code 2: Download & Transcribe (Python)**

⚠️ **Problem**: Zapier Code has 10-second timeout

**Solution**: Skip transcription in Zapier, or use external service

**Simplified Version** (without transcription):
```python
# Just pass the data through
output = {
    "call_id": input_data.get("call_id"),
    "customer_number": input_data.get("from_number"),
    "agent_number": input_data.get("to_number"),
    "duration": f"{int(input_data.get('duration', 0)) // 60}m {int(input_data.get('duration', 0)) % 60}s",
    "call_time": input_data.get("call_time"),
    "recording_url": input_data.get("recording_url"),
    "concern": "Call inquiry - transcription pending",
    "mood": "Neutral"
}

return output
```

---

## 🎫 Zapier → Zoho Desk Action Setup

### **Action 1: Create Ticket**

| Zoho Desk Field | Zapier Value |
|-----------------|--------------|
| **Department** | Your department |
| **Subject** | `Call from {{customer_number}}` |
| **Description** | See template below |
| **Contact Phone** | `{{customer_number}}` |
| **Priority** | Medium |
| **Channel** | Phone |
| **Status** | Open |

**Description Template:**
```
Call from {{customer_number}}

📞 Call Details:
• Time: {{call_time}}
• Duration: {{duration}}
• Agent: {{agent_number}}

🎯 Concern: {{concern}}
🎧 Recording: {{recording_url}}

Call ID: {{call_id}}
```

### **Action 2: Add Comment (Note)**

**Only if you have transcription:**

| Field | Value |
|-------|-------|
| **Ticket ID** | `{{ticket_id}}` from previous step |
| **Content** | `{{transcription}}` |
| **Public** | No (private note) |

---

## 🚀 Recommended Approach

Since Zapier has limitations (10-second timeout, no audio processing), here's the **best approach**:

### **Hybrid Solution: Zapier + Simple Middleware**

```
Exotel → Zapier → Your Middleware → Zoho Desk
```

**Why?**
- ✅ Zapier handles the workflow
- ✅ Middleware handles heavy lifting (transcription)
- ✅ Both are cloud-based
- ✅ No local processor needed

---

## 💡 Three Options for You

### **Option 1: Pure Zapier (Simple, No Transcription)**

✅ **Pros:**
- No coding required
- Easy to set up
- No servers needed

❌ **Cons:**
- No transcription (only recording URL)
- 10-second timeout limit

**Good for:** Quick setup, tickets with recording links

---

### **Option 2: Zapier + Middleware (Recommended)**

✅ **Pros:**
- Full transcription
- Concern analysis
- Cloud-based (no local processor)

❌ **Cons:**
- Need to deploy middleware (Railway/Render/Fly.io)
- Slightly more complex

**Good for:** Production use, full features

**Middleware**: Deploy `zoho_call_processor.py` to Railway/Render, expose webhook endpoint

---

### **Option 3: Exotel Webhook → Middleware → Zoho**

Skip Zapier entirely:

✅ **Pros:**
- Direct integration
- Full control
- No Zapier costs

❌ **Cons:**
- Need to deploy and maintain middleware
- Configure Exotel webhooks

**Good for:** Technical users, direct control

---

## 🔧 Which Should You Choose?

### **Choose Option 1 if:**
- You don't need transcriptions
- Recording URL in ticket is enough
- You want the simplest setup

### **Choose Option 2 if:**
- You need transcriptions
- You want Zapier's workflow management
- You're okay deploying a small middleware

### **Choose Option 3 if:**
- You don't want to use Zapier
- You want full control
- You're comfortable with cloud deployment

---

## 📋 What I Can Create for You

Tell me which option you prefer, and I'll create:

1. **Option 1**: Complete Zapier workflow guide with step-by-step screenshots
2. **Option 2**: Middleware with webhook + Zapier integration guide
3. **Option 3**: Direct Exotel → Middleware → Zoho solution

---

## 🤔 My Recommendation

For **Zapier-based** solution: **Option 2** (Zapier + Middleware)

**Why?**
- You get transcriptions ✅
- Zapier manages the workflow ✅
- Middleware handles heavy processing ✅
- Cloud-based (no local PC needed) ✅

**Flow:**
```
1. Schedule triggers every 5 min
2. Zapier calls your middleware webhook
3. Middleware:
   - Fetches new calls
   - Downloads recordings
   - Transcribes
   - Analyzes
   - Returns data to Zapier
4. Zapier creates Zoho ticket with transcription
```

---

## ❓ What Would You Like?

**Tell me:**
1. Do you need transcriptions in tickets? (Yes/No)
2. Are you okay deploying a small middleware to Railway/Render? (Yes/No)
3. Do you have Exotel webhook support? (Yes/No)

I'll create the exact solution you need! 🚀

