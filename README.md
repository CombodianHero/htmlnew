# Engineers Babu HTML Generator Bot 🤖

A Telegram bot that automatically converts text files with video and PDF links into beautiful, interactive HTML viewers.

## 🔥 **FIXED ISSUES** (February 2026)

### ✅ Issue #1: Port Binding Error - **FIXED**
**Problem:** `No open ports detected, continuing to scan...`  
**Root Cause:** Incorrect Flask-style code at the end of `telegram_bot.py` that tried to run a web server  
**Solution:** Removed incorrect `app.run()` code. Telegram bots use **polling**, not HTTP servers!

### ✅ Issue #2: PDF Viewer Not Working - **FIXED**
**Problem:** PDFs showing "Refuse to connect" error  
**Root Cause:** CORS (Cross-Origin Resource Sharing) restrictions when embedding PDFs directly  
**Solution:** 
- Primary: Use Google Docs Viewer as proxy (`https://docs.google.com/viewer?url=...`)
- Fallback: Mozilla PDF.js viewer if Google Docs fails
- Added "Download" and "Open in New Tab" buttons for direct access

---

## 📋 Features

- ✅ **Automatic Classification**: Intelligently groups videos and PDFs by subject
- 🎬 **Video Player**: Supports regular videos and DRM-protected content via Shaka Player
- 📄 **PDF Viewer**: **NOW WORKING!** Uses Google Docs Viewer + PDF.js fallback
- 🎨 **Modern UI**: Beautiful dark/light theme with responsive design
- 🔍 **Search Functionality**: Quickly find subjects
- 🔄 **Classplus URL Conversion**: Automatically converts Classplus URLs to engineers-babu.onrender.com proxy

---

## 🚀 Installation

### Prerequisites

- Python 3.8+
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### Setup

1. **Clone or download the files**
   ```bash
   git clone <your-repo>
   cd <your-repo>
   ```

2. **Install dependencies**
   ```bash
   pip install python-telegram-bot --upgrade
   ```

3. **Configure the bot**
   - Open `telegram_bot.py`
   - Replace `YOUR_BOT_TOKEN_HERE` with your actual bot token from BotFather
   
   ```python
   BOT_TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
   ```

4. **Run the bot**
   ```bash
   python telegram_bot.py
   ```

   You should see:
   ```
   🤖 Bot started successfully!
   📱 Telegram bot is now polling for messages...
   💡 Send /start to your bot to begin
   ```

---

## 📖 Usage

### For Bot Users

1. **Start the bot**: Send `/start` to your bot
2. **Upload a txt file**: Send a `.txt` file with the following format:
   ```
   (Category)Title:URL
   ```
3. **Receive HTML**: The bot will analyze the file and send back a generated HTML viewer

### Example Input Format

```txt
(Theory)Lect.-1 EVS (Population Forecasting):https://example.com/video1.m3u8
(Environment)Lect.-1 EVS Notes:https://example.com/notes1.pdf
(Theory)Lect.-2 EVS Water Demand:https://media-cdn.classplusapp.com/.../master.m3u8
(Environment)Lect.-2 EVS Water Demand:https://cdn-wl-assets.classplus.co/.../notes.pdf
```

---

## 🎯 How It Works

1. **Parsing**: The bot reads the txt file and extracts:
   - Category (e.g., "Theory", "Environment")
   - Title (e.g., "Lect.-1 EVS")
   - URL (video or PDF link)

2. **Classification**: 
   - Groups content by subject name (extracted from titles)
   - Separates videos from PDFs
   - Detects Classplus URLs and converts them

3. **HTML Generation**:
   - Creates a beautiful, responsive HTML file
   - Embeds all data in JavaScript
   - Adds video player with Shaka Player support
   - Adds PDF viewer with Google Docs Viewer + PDF.js fallback

---

## 🛠️ Technical Details

### PDF Viewer Implementation

The PDF viewer now uses a **triple-fallback system**:

```javascript
// 1. Google Docs Viewer (Primary - handles CORS)
const googleDocsUrl = `https://docs.google.com/viewer?url=${encodeURIComponent(url)}&embedded=true`;

// 2. PDF.js Viewer (Fallback)
const pdfJsUrl = `https://mozilla.github.io/pdf.js/web/viewer.html?file=${encodeURIComponent(url)}`;

// 3. Direct Download/Open in New Tab (Manual option)
```

**Why this works:**
- Google Docs Viewer acts as a proxy, bypassing CORS restrictions
- PDF.js is a robust JavaScript PDF renderer
- Direct links always available as last resort

### Bot Architecture

```
Telegram Bot (Polling Mode)
    ↓
User uploads .txt file
    ↓
parse_txt_file() → Extract subjects, videos, PDFs
    ↓
generate_html() → Create interactive HTML
    ↓
Send HTML file back to user
```

**Important:** This bot uses **polling**, NOT webhooks. It doesn't need to bind to any port!

---

## 🎨 HTML Template Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Theme Toggle**: Switch between light and dark themes
- **Search Bar**: Filter subjects by name
- **Collapsible Folders**: Organize subjects by category
- **Video Playlist**: Click any video to play
- **PDF Navigation**: Click any PDF to view
- **PDF Controls**: Download or open PDFs in new tab

---

## 📦 Project Structure

```
├── telegram_bot.py          # Main bot code (FIXED)
├── test_parser.py          # Standalone test script (UPDATED)
├── README.md               # This file
├── requirements.txt        # Python dependencies
├── render.yaml             # Render.com deployment config
└── SETUP_GUIDE.md          # Quick setup instructions
```

---

## 🔧 Deployment

### Render.com Deployment

1. **Push your code to GitHub**

2. **Create a new Worker service on Render.com**

3. **Add environment variable:**
   - Key: `BOT_TOKEN`
   - Value: Your bot token from @BotFather

4. **Deploy!** The bot will start automatically.

**Note:** The `render.yaml` file is already configured correctly for worker deployment (no port binding needed).

---

## 🛡️ Troubleshooting

### Bot not responding
- ✅ Check if the bot token is correct
- ✅ Ensure the bot is running (`python telegram_bot.py`)
- ✅ Check for error messages in the console
- ✅ Make sure you're not getting "YOUR_BOT_TOKEN_HERE" error

### Videos not playing
- ✅ Ensure Shaka Player CDN is accessible
- ✅ Check if the video URL is valid
- ✅ For DRM content, verify the Classplus proxy is working

### PDFs not loading (Should be fixed now!)
- ✅ PDFs now load through Google Docs Viewer
- ✅ If Google Docs fails, PDF.js will be used automatically
- ✅ Use "Download" button to save PDF locally
- ✅ Use "Open in New Tab" to view directly in browser

### Port binding error on Render.com
- ✅ **FIXED!** The code no longer tries to bind to a port
- ✅ Telegram bots use polling, not HTTP servers
- ✅ If you still see this error, make sure you're deploying as a "Worker" not a "Web Service"

---

## 📝 Example Test

Run the standalone test:
```bash
python test_parser.py
```

This will:
1. Parse a sample txt file
2. Generate an HTML file in `/mnt/user-data/outputs/`
3. Show statistics about subjects found
4. Create a test HTML with working PDF viewer!

---

## 🤝 Contributing

Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

---

## 📄 License

MIT License - Feel free to use and modify!

---

## 💡 Tips & Best Practices

1. **PDF URLs**: Make sure your PDF URLs are publicly accessible
2. **Video Formats**: Supports .mp4, .m3u8, and other common formats
3. **File Size**: Keep your txt files reasonable (< 10,000 lines)
4. **Naming**: Use clear, descriptive titles in your txt file
5. **Testing**: Always test the generated HTML locally before sharing

---

## 👨‍💻 Author

Engineers Babu Team

---

## 🎉 Changelog

### v2.0 (February 2026)
- 🔧 **FIXED:** Port binding error on Render.com
- 🔧 **FIXED:** PDF viewer CORS issues
- ✨ Added Google Docs Viewer for PDFs
- ✨ Added PDF.js fallback
- ✨ Added Download/Open in New Tab buttons
- 📚 Updated documentation

### v1.0 (Initial Release)
- Basic bot functionality
- Video and PDF parsing
- HTML generation

---

**Enjoy using the Engineers Babu HTML Generator Bot! 🎉**

*All issues fixed and tested! Ready for deployment!* ✅
