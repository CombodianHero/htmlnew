# Engineers Babu HTML Generator Bot 🤖

A Telegram bot that automatically converts text files with video and PDF links into beautiful, interactive HTML viewers with advanced security features.

## 🔥 New Features

- ✅ **Fixed Video Player**: No scrolling inside video player, responsive 16:9 aspect ratio
- 🔒 **Security Features**: Right-click disabled, inspect disabled, F12 blocked
- 🆔 **Dynamic Watermark**: Shows user's Telegram ID and name on videos
- 📱 **Mobile Optimized**: Fullscreen support with auto-rotate handling
- 🖼️ **PDF Fullscreen Modal**: PDFs open in fullscreen overlay
- 🎯 **Auto-Scroll**: Automatically scrolls to video section when playing
- 🎨 **Modern UI**: Beautiful dark/light theme with responsive design

## 📋 Features

- ✅ **Automatic Classification**: Intelligently groups videos and PDFs by subject
- 🎬 **Video Player**: Supports regular videos and DRM-protected content via Shaka Player
- 📄 **PDF Viewer**: Integrated fullscreen PDF viewer with modal
- 🎨 **Modern UI**: Beautiful dark/light theme with responsive design
- 🔍 **Search Functionality**: Quickly find subjects
- 📄 **Classplus URL Conversion**: Automatically converts Classplus URLs to proxy
- 🔒 **Content Protection**: Right-click disabled, inspect blocked
- 🆔 **User Watermark**: Each HTML file is personalized with user info

## 🚀 Installation

### Prerequisites

- Python 3.8+
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### Local Setup

1. **Clone or download the files**
   ```bash
   git clone <your-repo>
   cd <your-repo>
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot**
   - Set environment variable:
   ```bash
   export BOT_TOKEN="your_bot_token_here"
   ```
   
   Or edit `telegram_bot.py`:
   ```python
   BOT_TOKEN = "your_bot_token_here"
   ```

4. **Run the bot**
   ```bash
   python telegram_bot.py
   ```

### Deploy to Render

1. **Create a new Web Service** on [Render.com](https://render.com)

2. **Connect your GitHub repository**

3. **Add Environment Variable**:
   - Key: `BOT_TOKEN`
   - Value: Your Telegram bot token

4. **Deploy**: Render will automatically use `render.yaml` for configuration

## 📖 Usage

### For Bot Users

1. **Start the bot**: Send `/start` to your bot
2. **Upload a txt file**: Send a `.txt` file with the following format:
   ```
   (Category)Title:URL
   ```
3. **Receive HTML**: The bot will generate a personalized HTML viewer

### Example Input Format

```txt
(Theory)Lect.-1 EVS (Population Forecasting):https://example.com/video1.m3u8
(Environment)Lect.-1 EVS Notes:https://example.com/notes1.pdf
(Theory)Lect.-2 EVS Water Demand:https://media-cdn.classplusapp.com/.../master.m3u8
(Environment)Lect.-2 EVS Water Demand:https://cdn-wl-assets.classplus.co/.../notes.pdf
```

### How It Works

1. **Parsing**: Extracts category, title, and URL from each line
2. **Classification**: Groups content by subject name
3. **HTML Generation**: Creates personalized HTML with user watermark
4. **Security**: Adds protection against unauthorized access

## 🎯 Key Features Explained

### Fixed Video Player Layout
- Responsive 16:9 aspect ratio
- No internal scrolling
- Smooth playback experience

### PDF Fullscreen Modal
- Click any PDF to open in fullscreen
- Easy close button
- Smooth transitions

### User Watermark
- Dynamic watermark with Telegram user ID and name
- Cannot be removed or hidden
- Visible on all videos

### Security Features
- Right-click disabled
- Context menu blocked
- F12 / Inspect disabled
- Ctrl+Shift+I/J blocked
- Ctrl+U (view source) blocked

### Mobile Support
- Fullscreen video support
- Auto-rotate handling
- Touch-optimized interface

### Auto-Scroll
- Clicking a subject scrolls to video player
- Clicking a video scrolls to player
- Smooth scroll animations

## 🛠️ Project Structure

```
├── telegram_bot.py          # Main bot code
├── test_parser.py          # Standalone test script
├── README.md               # This file
├── requirements.txt        # Python dependencies
└── render.yaml            # Render deployment config
```

## 📦 Dependencies

```txt
python-telegram-bot>=20.0
```

## 🎨 HTML Template Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Theme Toggle**: Switch between light and dark themes
- **Search Bar**: Filter subjects by name
- **Collapsible Folders**: Organize subjects by category
- **Video Playlist**: Click any video to play
- **PDF Modal**: Fullscreen PDF viewer
- **Watermark**: Dynamic user identification

## 🔧 Testing

### Test Locally

Run the test script:
```bash
python test_parser.py
```

This will:
1. Parse sample data
2. Generate an HTML file in `/mnt/user-data/outputs/`
3. Show statistics about subjects found

### Test the Bot

1. Start the bot: `python telegram_bot.py`
2. Send `/start` to your bot
3. Upload a test `.txt` file
4. Download and open the generated HTML

## 🌐 Deployment

### Render.com (Recommended)

1. Push code to GitHub
2. Connect to Render
3. Add `BOT_TOKEN` environment variable
4. Deploy automatically

### Heroku

```bash
heroku create your-app-name
heroku config:set BOT_TOKEN=your_token_here
git push heroku main
```

### Railway

1. Connect GitHub repository
2. Add `BOT_TOKEN` variable
3. Deploy

## 🛡️ Security Features

1. **Right-click Protection**: Prevents copying content
2. **Inspect Disabled**: Blocks developer tools
3. **Keyboard Shortcuts Blocked**: F12, Ctrl+Shift+I/J/U disabled
4. **Text Selection Disabled**: Prevents text copying
5. **User Watermark**: Tracks file ownership

## 📱 Mobile Features

1. **Fullscreen Support**: Videos can go fullscreen
2. **Orientation Lock**: Attempts to lock landscape mode
3. **Touch Optimized**: Large touch targets
4. **Responsive Layout**: Adapts to screen size

## 🆕 Changelog

### Version 2.0
- ✅ Fixed video player layout (no scrolling)
- ✅ PDF fullscreen modal implementation
- ✅ Auto-scroll to video section
- ✅ Dynamic user watermark
- ✅ Security features (right-click, inspect disabled)
- ✅ Mobile fullscreen support
- ✅ Fixed port error for Render deployment

### Version 1.0
- Initial release
- Basic HTML generation
- Video and PDF support

## 🤝 Contributing

Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📄 License

MIT License - Feel free to use and modify!

## 👨‍💻 Author

Engineers Babu Team

## 🙏 Support

If you encounter any issues:
1. Check the console logs
2. Verify your bot token
3. Ensure all URLs are accessible
4. Test with the provided test script

---

**Enjoy using the Engineers Babu HTML Generator Bot! 🎉**
