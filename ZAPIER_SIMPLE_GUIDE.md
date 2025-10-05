# 🔄 Simple Zapier → Zoho Desk Setup (No Transcription)

## ✨ Simplest Solution - 15 Minutes Setup

This creates Zoho Desk tickets with call details and recording URLs (no transcription).

---

## 🎯 What You'll Get

✅ Automatic Zoho Desk tickets for each call  
✅ Call details (time, duration, phone numbers)  
✅ Recording URL (click to listen)  
✅ Auto-linked to contacts  
❌ No transcription (recording URL only)

---

## 🧩 Step-by-Step Setup

### **Step 1: Connect Zoho Desk to Zapier**

1. Go to [Zapier](https://zapier.com/) → Create Zap
2. Skip trigger for now
3. Click **"+ Add Step"** → Choose **"Zoho Desk"**
4. Action: **"Create Ticket"**
5. Click **"Sign in to Zoho Desk"**
6. Authorize Zapier
7. Select your **Organization** and **Department**

✅ **Zoho Desk connected!**

---

### **Step 2: Set Up Schedule Trigger**

1. Go back to trigger
2. Choose **"Schedule by Zapier"**
3. Event: **"Every X Minutes"**
4. Interval: **5 minutes** (or your preference)
5. Click **"Continue"**

---

### **Step 3: Add Python Code to Fetch Calls**

1. Click **"+ Add Step"**
2. Choose **"Code by Zapier"**
3. Event: **"Run Python"**
4. Set up code:

```python
import requests
from datetime import datetime, timedelta

# ============================================
# CONFIGURE THESE WITH YOUR CREDENTIALS
# ============================================
EXOTEL_SID = "abc6862"  # Your Exotel SID
EXOTEL_KEY = "your_api_key"  # Your Exotel API Key
EXOTEL_TOKEN = "your_api_token"  # Your Exotel API Token

# Fetch recent calls
url = f"https://api.exotel.com/v1/Accounts/{EXOTEL_SID}/Calls.json"
auth = (EXOTEL_KEY, EXOTEL_TOKEN)
params = {"PageSize": 5, "Page": 0}

response = requests.get(url, auth=auth, params=params, timeout=5)

if response.status_code == 200:
    calls = response.json().get("Calls", [])
    
    # Find first completed call with recording
    for call in calls:
        if call.get("Status") == "completed" and call.get("RecordingUrl"):
            from_num = call.get("From", {}).get("PhoneNumber", "Unknown")
            to_num = call.get("To", {}).get("PhoneNumber", "Unknown")
            duration_sec = int(call.get("Duration", 0))
            
            output = {
                "call_id": call.get("Sid"),
                "customer_number": from_num,
                "agent_number": to_num,
                "duration": f"{duration_sec // 60}m {duration_sec % 60}s",
                "call_time": call.get("DateCreated", "Unknown"),
                "recording_url": call.get("RecordingUrl", ""),
                "status": call.get("Status"),
                "direction": "Incoming" if "+" in from_num else "Outgoing"
            }
            
            # Only process if not already processed
            # You can use Zapier's built-in deduplication
            break
    else:
        output = {"error": "No new calls"}
else:
    output = {"error": f"API Error: {response.status_code}"}

# Define output for Zapier
if 'output' not in locals():
    output = {"error": "No output generated"}
```

5. Click **"Continue"**
6. Click **"Test Step"** to verify

---

### **Step 4: Add Filter (Optional but Recommended)**

1. Click **"+ Add Step"**
2. Choose **"Filter by Zapier"**
3. Condition: **"Only continue if..."**
   - Field: `Error`
   - Condition: `Does not exist`

This prevents creating tickets when no new calls exist.

---

### **Step 5: Create Zoho Desk Ticket**

1. Click **"+ Add Step"**
2. Choose **"Zoho Desk"**
3. Action: **"Create Ticket"**
4. Configure fields:

| Field | Value |
|-------|-------|
| **Department** | Select your department |
| **Contact Phone** | `{{customer_number}}` |
| **Subject** | `Call from {{customer_number}}` |
| **Status** | Open |
| **Priority** | Medium |
| **Channel** | Phone |
| **Description** | See template below |

**Description Template:**
```
Call from {{customer_number}}

📞 Call Details:
• Customer: {{customer_number}}
• Agent: {{agent_number}}
• Time: {{call_time}}
• Duration: {{duration}}
• Direction: {{direction}}

🎧 Recording:
{{recording_url}}

Call ID: {{call_id}}

---
Auto-generated via Zapier
```

5. Click **"Continue"**
6. Click **"Test Step"**

---

### **Step 6: (Optional) Add Comment with Recording Link**

1. Click **"+ Add Step"**
2. Choose **"Zoho Desk"**
3. Action: **"Add Comment to Ticket"**
4. Configure:
   - **Ticket ID**: `{{id}}` from previous step
   - **Content**: `🎧 Call Recording: {{recording_url}}`
   - **Public**: No (internal note)

---

### **Step 7: Turn On Zap**

1. Name your Zap: "Exotel → Zoho Desk Tickets"
2. Click **"Turn On Zap"**

✅ **Done!**

---

## 🎯 What Happens Now

Every 5 minutes:
1. ✅ Zapier checks Exotel for new calls
2. ✅ If new call found → Create Zoho ticket
3. ✅ Ticket includes all call details + recording URL
4. ✅ Contact auto-created/linked by phone number

---

## 🐛 Troubleshooting

### **"API Error: 401"**
→ Check Exotel credentials (SID, Key, Token)

### **"No new calls"**
→ Normal, means no new calls since last check

### **"Zoho Desk: Contact not found"**
→ Enable "Create Contact if not found" in Zoho Desk action

### **Zap running but no tickets**
→ Check Filter step, might be blocking tickets

### **Duplicate tickets**
→ Add **Storage by Zapier** to track processed calls

---

## 🔥 Upgrade: Add Deduplication

To prevent duplicate tickets:

1. Add **"Storage by Zapier"** before Zoho Desk action
2. **Get Value**: Key = `last_call_id`
3. Add **Filter**: Only continue if `{{call_id}}` ≠ stored value
4. After Zoho ticket created, **Set Value**: Key = `last_call_id`, Value = `{{call_id}}`

---

## 📊 What Gets Created

**Ticket Example:**

**Subject:** `Call from 9876543210`

**Description:**
```
Call from 9876543210

📞 Call Details:
• Customer: 9876543210
• Agent: 09631084471
• Time: 2025-10-05 12:30:00
• Duration: 2m 45s
• Direction: Incoming

🎧 Recording:
https://recordings.exotel.com/abc6862/abc123.mp3

Call ID: abc123def456

---
Auto-generated via Zapier
```

---

## ⏱️ Setup Time: ~15 minutes

---

## 💡 Limitations

- ❌ No transcription (recording URL only)
- ⚠️ 5-minute polling (not real-time)
- ⚠️ Zapier free plan: 100 tasks/month

---

## 🚀 Next Steps

**Want transcriptions?**
→ See `ZAPIER_WITH_TRANSCRIPTION.md` (coming next)

**Want real-time?**
→ Set up Exotel webhooks (if supported)

**Want to test?**
1. Make a test call on Exotel
2. Wait 5 minutes
3. Check Zoho Desk for new ticket!

---

## ✅ Summary

You now have:
- ✅ Automated ticket creation
- ✅ Call details in tickets
- ✅ Recording URLs
- ✅ Contact auto-linking
- ✅ No server/PC needed

**All running in Zapier's cloud!** 🎉

