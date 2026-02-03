# 🚀 DEPLOYMENT GUIDE - Smart Grouping Bot

## 📦 Files for Deployment

You have **3 essential files** for deployment:

1. **telegram_bot.py** - Main bot code (with smart grouping)
2. **requirements.txt** - Python dependencies
3. **render.yaml** - Render.com configuration

---

## ⚡ QUICK DEPLOY - 3 Steps

### Step 1️⃣: Push to GitHub

```bash
# Create a new repository or use existing one
git init
git add telegram_bot.py requirements.txt render.yaml
git commit -m "Smart grouping bot - ready for deployment"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Step 2️⃣: Deploy on Render.com

1. Go to https://render.com
2. Click **"New +"** → **"Worker"** (NOT Web Service!)
3. Connect your GitHub repository
4. Render will auto-detect `render.yaml`

### Step 3️⃣: Set Environment Variable

In Render.com dashboard:
1. Go to **Environment** tab
2. Add environment variable:
   - **Key:** `BOT_TOKEN`
   - **Value:** `<your-bot-token-from-@BotFather>`
3. Click **"Save Changes"**

**Done!** Your bot will deploy automatically! ✅

---

## 📋 Detailed Instructions

### A. Get Your Bot Token

1. Open Telegram
2. Search for **@BotFather**
3. Send `/newbot`
4. Follow instructions to create your bot
5. Copy the token (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### B. Prepare Your Repository

**Option 1: New Repository**
```bash
# In the folder with your bot files:
git init
git add telegram_bot.py requirements.txt render.yaml
git commit -m "Initial commit - Smart grouping bot"

# Create repo on GitHub, then:
git remote add origin https://github.com/yourusername/your-repo.git
git branch -M main
git push -u origin main
```

**Option 2: Existing Repository**
```bash
# Copy the 3 files to your existing repo
cp telegram_bot.py /path/to/your/repo/
cp requirements.txt /path/to/your/repo/
cp render.yaml /path/to/your/repo/

cd /path/to/your/repo/
git add telegram_bot.py requirements.txt render.yaml
git commit -m "Added smart grouping bot"
git push
```

### C. Deploy on Render.com

1. **Create Account** (if needed)
   - Go to https://render.com
   - Sign up with GitHub

2. **Create New Worker**
   - Click **"New +"**
   - Select **"Worker"** (Important: NOT "Web Service"!)
   - Connect your GitHub account if not already connected
   - Select your repository
   - Click **"Connect"**

3. **Configure (Auto-detected)**
   - Render will read `render.yaml` automatically
   - Name: `engineers-babu-bot`
   - Type: `worker`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python telegram_bot.py`

4. **Add Bot Token**
   - Go to **"Environment"** tab
   - Click **"Add Environment Variable"**
   - Key: `BOT_TOKEN`
   - Value: Your bot token from @BotFather
   - Click **"Save Changes"**

5. **Deploy!**
   - Click **"Manual Deploy"** → **"Deploy latest commit"**
   - Wait 1-2 minutes for deployment

### D. Verify Deployment

Check the **Logs** tab on Render.com. You should see:

```
🤖 Bot started successfully!
📱 Telegram bot is now polling for messages...
💡 Send /start to your bot to begin
```

If you see this, **you're done!** ✅

---

## 🧪 Test Your Bot

1. Open Telegram
2. Search for your bot (the name you gave it)
3. Send `/start`
4. You should see the welcome message
5. Upload a `.txt` file
6. Get back an HTML file with smart grouping!

---

## ⚙️ File Contents Explained

### 1. telegram_bot.py
- Main bot code
- Smart grouping feature included
- PDF viewer fixes included
- Port binding fixes included
- Ready to run!

### 2. requirements.txt
```
python-telegram-bot>=20.0
```
- Only dependency needed
- Will auto-install during deployment

### 3. render.yaml
```yaml
services:
  - type: worker
    name: engineers-babu-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python telegram_bot.py
    envVars:
      - key: BOT_TOKEN
        sync: false
```
- Tells Render.com how to deploy
- Sets it as a **worker** (not web service)
- No port binding needed

---

## 🔧 Troubleshooting

### ❌ Error: "No module named 'telegram'"
**Solution:** Render.com didn't install dependencies
```bash
# Check requirements.txt exists and contains:
python-telegram-bot>=20.0
```

### ❌ Error: "Please set BOT_TOKEN"
**Solution:** Environment variable not set
1. Go to Render.com dashboard
2. Environment tab
3. Add `BOT_TOKEN` with your token
4. Save and redeploy

### ❌ Error: "No open ports detected"
**Solution:** You deployed as "Web Service" instead of "Worker"
1. Delete the service
2. Create new **Worker** service
3. Or edit `render.yaml` to specify `type: worker`

### ❌ Bot doesn't respond
**Solution:** Check logs on Render.com
1. Go to Logs tab
2. Look for error messages
3. Make sure you see "Bot started successfully!"

### ❌ Deployment failed
**Solution:** Check the build logs
1. Common issues:
   - Wrong Python version (should use 3.8+)
   - Missing requirements.txt
   - Syntax errors in code

---

## 🔄 Update Deployment

When you make changes:

```bash
# Make your changes to telegram_bot.py
git add telegram_bot.py
git commit -m "Updated bot"
git push

# Render.com will auto-deploy the changes!
```

Or manually trigger deployment:
1. Go to Render.com dashboard
2. Click **"Manual Deploy"**
3. Select **"Deploy latest commit"**

---

## 📊 Monitor Your Bot

### Check Logs
```
Render.com → Your Service → Logs tab

You should see:
✅ Bot started successfully!
✅ Processing messages
✅ No errors
```

### Restart Bot
```
Render.com → Your Service → Settings → Manual Deploy
Or: Settings → Suspend Service, then Resume
```

---

## 💰 Pricing

**Render.com Free Tier:**
- ✅ 750 hours/month free
- ✅ Perfect for a bot running 24/7
- ✅ Automatic deployments
- ✅ No credit card required

**Your bot uses minimal resources:**
- CPU: Very low (only active when processing files)
- Memory: ~100-200 MB
- Bandwidth: Minimal

**Free tier is more than enough!** ✅

---

## 🎯 Checklist

Before deploying, make sure:

- [ ] You have a GitHub account
- [ ] You have a Render.com account
- [ ] You got your bot token from @BotFather
- [ ] You have these 3 files:
  - [ ] telegram_bot.py
  - [ ] requirements.txt
  - [ ] render.yaml
- [ ] Files are pushed to GitHub
- [ ] Created a **Worker** service (not Web Service!)
- [ ] Added `BOT_TOKEN` environment variable
- [ ] Deployment shows "Live" status
- [ ] Logs show "Bot started successfully!"

---

## 🎉 You're Ready!

Once deployed:
1. ✅ Bot runs 24/7 automatically
2. ✅ Auto-restarts if it crashes
3. ✅ Auto-deploys when you push to GitHub
4. ✅ Smart grouping works automatically
5. ✅ PDF viewer works perfectly
6. ✅ No port binding errors

**Just upload a .txt file and get organized HTML!** 🚀

---

## 📞 Support

If you need help:

1. **Check Render.com logs** - Most issues shown here
2. **Verify bot token** - Make sure it's correct
3. **Check GitHub** - Make sure files are uploaded
4. **Review this guide** - Step-by-step instructions

Common issues are covered in the Troubleshooting section above.

---

## 🔐 Security Note

**Never commit your bot token to GitHub!**

✅ **Correct way:**
```bash
# In Render.com environment variables:
BOT_TOKEN=your_actual_token_here
```

❌ **Wrong way:**
```python
# Don't do this in telegram_bot.py:
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
```

The code already handles this correctly:
```python
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
```
- Gets token from environment variable
- Shows error if not set
- Safe to commit to GitHub

---

**Happy deploying!** 🎉

*Your bot is production-ready with all fixes and smart grouping!*
