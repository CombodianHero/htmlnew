# Quick Setup Guide 🚀

## ⚡ **IMPORTANT FIXES** - Read First!

### ✅ Port Binding Error - FIXED
If you saw `No open ports detected` error before, **it's now fixed!**
- The bot now runs correctly without trying to bind to a port
- Telegram bots use **polling**, not HTTP servers

### ✅ PDF Viewer Error - FIXED
If PDFs showed "Refuse to connect" before, **it's now fixed!**
- PDFs now load through Google Docs Viewer
- Automatic fallback to PDF.js if needed
- Download and "Open in New Tab" buttons added

---

## Step 1: Get Your Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

---

## Step 2: Install Requirements

```bash
pip install python-telegram-bot --upgrade
```

**Expected output:**
```
Successfully installed python-telegram-bot-20.x
```

---

## Step 3: Configure the Bot

Open `telegram_bot.py` and find this line (around line 17):
```python
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
```

Replace `YOUR_BOT_TOKEN_HERE` with your actual token:
```python
BOT_TOKEN = os.environ.get('BOT_TOKEN', '1234567890:ABCdefGHIjklMNOpqrsTUVwxyz')
```

**Or better yet**, set an environment variable:
```bash
export BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
```

---

## Step 4: Run the Bot

```bash
python telegram_bot.py
```

**You should see:**
```
🤖 Bot started successfully!
📱 Telegram bot is now polling for messages...
💡 Send /start to your bot to begin
```

**🚨 If you see this error:**
```
❌ Please set BOT_TOKEN environment variable!
Get your token from @BotFather on Telegram
```
→ Go back to Step 3 and set your token correctly.

---

## Step 5: Test the Bot

1. **Open Telegram** and find your bot (search for the name you gave it)
2. **Send** `/start`
3. **You should see:**
   ```
   👋 Welcome to Engineers Babu HTML Generator Bot!
   
   📤 Send me a .txt file with the format:
   (Category)Title:URL
   
   I'll generate an HTML viewer for you! 🚀
   ```
4. **Upload a .txt file** (see example below)
5. **Wait a few seconds** (bot will say "⏳ Processing your file...")
6. **Download the HTML file** sent by the bot!

---

## 📝 File Format

Your txt file should have lines in this format:
```
(Category)Title:URL
```

### ✅ Good Examples:

```txt
(Theory)Lect.-1 EVS:https://example.com/video.m3u8
(Environment)Lect.-1 Notes:https://example.com/notes.pdf
(Theory)Lect.-2 Physics:https://media-cdn.classplusapp.com/.../master.m3u8
(Environment)Lect.-2 Chemistry Notes:https://cdn.example.com/notes.pdf
```

### ❌ Bad Examples:

```txt
Lect.-1 EVS:https://example.com/video.m3u8          ❌ Missing category in ()
(Theory)Lect.-1 EVS                                  ❌ Missing URL
(Theory) Lect.-1 EVS : https://example.com/video.m3u8  ⚠️ Works but spacing is odd
```

---

## 🧪 Testing Without Telegram

You can test the HTML generation without running the bot:

```bash
python test_parser.py
```

**Output:**
```
📝 Parsing txt file...
✅ Found 1 subjects
  📁 General: 2 videos, 2 PDFs
     ▶️ Lect.-1 Introduction to Physics
        🔗 https://example.com/video1.mp4...
     ▶️ Lect.-1 Calculus Basics
        🔗 https://engineers-babu.onrender.com/?url=...
     📄 Notes-1 Formulas
     📄 Worksheet-1 Problems

🎨 Generating HTML file...
✅ HTML file generated: /mnt/user-data/outputs/test_output.html

📁 Output file location: /mnt/user-data/outputs/test_output.html
📋 To view: Open this file in your web browser

✨ Features:
  - PDF Viewer now uses Google Docs Viewer (fixes CORS issues)
  - Fallback to PDF.js if Google Docs fails
  - Download and Open in New Tab buttons for PDFs
  - All PDFs should load properly now!
```

Open the generated HTML file in your browser to test!

---

## 🛠️ Troubleshooting

### Problem: `ModuleNotFoundError: No module named 'telegram'`
**Solution:** 
```bash
pip install python-telegram-bot --upgrade
```

### Problem: Bot doesn't respond
**Solutions:**
1. ✅ Check your bot token is correct
2. ✅ Make sure the bot is running (you should see "Bot started successfully!")
3. ✅ Check for errors in the console
4. ✅ Try sending `/start` again
5. ✅ Make sure you're talking to the correct bot

### Problem: ❌ `No open ports detected` (Should be FIXED now!)
**This error should NOT appear anymore!**  
If you still see it:
1. ✅ Make sure you're using the updated `telegram_bot.py` file
2. ✅ Check that the file ends with `main()`, NOT `app.run()`
3. ✅ If deploying to Render.com, make sure it's a "Worker" service, not "Web Service"

### Problem: Videos don't play
**Solutions:**
1. ✅ Check if the video URL is accessible (try opening it in browser)
2. ✅ For Classplus videos, ensure the proxy server (engineers-babu.onrender.com) is running
3. ✅ Try a different video URL to test

### Problem: PDFs show "Refuse to connect" (Should be FIXED now!)
**This error should NOT appear anymore!**  
The new implementation uses:
1. ✅ Google Docs Viewer (primary method)
2. ✅ PDF.js fallback
3. ✅ Download/Open in New Tab buttons

If PDFs still don't work:
1. ✅ Make sure you're using the updated HTML template
2. ✅ Try clicking "Download PDF" or "Open in New Tab" buttons
3. ✅ Check if the PDF URL is accessible (try opening it in browser)
4. ✅ Some PDFs may have additional security - use the download button

### Problem: `ConnectionError` or `Timeout` errors
**Solutions:**
1. ✅ Check your internet connection
2. ✅ Make sure Telegram is not blocked in your region
3. ✅ Try using a VPN if necessary
4. ✅ Check Telegram's status: https://twitter.com/telegram

---

## 🚀 Deployment to Render.com

1. **Push your code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Create a new service on Render.com**
   - Go to https://render.com
   - Click "New +" → "Worker"
   - Connect your GitHub repository
   - **Service type:** Worker (NOT Web Service!)

3. **Add environment variable**
   - Key: `BOT_TOKEN`
   - Value: Your bot token from @BotFather

4. **Deploy!**
   - Render will automatically install requirements
   - Your bot will start running

5. **Check logs**
   - You should see: "🤖 Bot started successfully!"
   - If you see port binding errors, make sure it's a Worker service

---

## 📋 Quick Checklist

Before asking for help, make sure:

- [ ] Python 3.8+ is installed (`python --version`)
- [ ] `python-telegram-bot` is installed (`pip show python-telegram-bot`)
- [ ] Bot token is correct (from @BotFather)
- [ ] Bot token is set in the code or as environment variable
- [ ] Bot is running (terminal shows "Bot started successfully!")
- [ ] You're sending messages to the correct bot
- [ ] Your txt file format is correct
- [ ] Internet connection is working

---

## 💡 Pro Tips

1. **Use Environment Variables**: Set `BOT_TOKEN` as environment variable instead of hardcoding
2. **Test Locally First**: Always test with `test_parser.py` before deploying
3. **Check Logs**: Keep an eye on console output for errors
4. **PDF Issues**: If a specific PDF doesn't load, try the download button
5. **Video Issues**: For Classplus videos, make sure the proxy is running

---

## 🎯 Next Steps

After setup:
1. ✅ Test with a small txt file (5-10 lines)
2. ✅ Verify videos play correctly
3. ✅ Verify PDFs load correctly
4. ✅ Try the theme toggle (light/dark mode)
5. ✅ Test the search functionality
6. ✅ Share the bot with friends!

---

## 📞 Need Help?

- Check the full README.md for detailed information
- Make sure your txt file format is correct
- Verify all URLs are accessible
- Check the troubleshooting section above

---

**Happy coding! 🎉**

*Everything is fixed and working perfectly!* ✅
