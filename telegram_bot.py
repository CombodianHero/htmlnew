import os
import re
import json
import urllib.parse
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7601635113:AAHjmE2yjru1sIIbAW6g56-sIc30cv4Tsm8')

def parse_txt_file(file_path):
    """Parse the txt file and classify subjects with videos and PDFs"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    subjects_dict = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Parse line: (Category)Title:URL
        match = re.match(r'\(([^)]+)\)(.+?):(https?://.+)', line)
        if not match:
            continue
        
        category = match.group(1).strip()
        title = match.group(2).strip()
        url = match.group(3).strip()
        
        # Extract subject name from title
        subject_match = re.search(r'(?:Lect[.-]?\d+\s+)(.+?)(?:\s*\(|$)', title)
        if subject_match:
            subject_name = subject_match.group(1).strip()
        else:
            subject_match = re.search(r'Lect[.-]?\d+\s+(.+)', title)
            if subject_match:
                subject_name = subject_match.group(1).strip()
            else:
                subject_name = "General"
        
        # Clean up subject name
        subject_name = re.sub(r'\s+', ' ', subject_name)
        
        # Determine if it's video or PDF
        is_pdf = url.endswith('.pdf')
        is_video = not is_pdf
        
        # Process Classplus URLs through API
        if is_video and 'classplus' in url.lower():
            url = f"https://engineers-babu-player-0ppl.onrender.com/?url={urllib.parse.quote(url)}"
        
        # Initialize subject if not exists
        if subject_name not in subjects_dict:
            subjects_dict[subject_name] = {
                'videos': [],
                'pdfs': []
            }
        
        # Add to appropriate list
        if is_video:
            subjects_dict[subject_name]['videos'].append({
                'title': title,
                'src': url,
                'drm': 'classplus' in match.group(3).lower()
            })
        else:
            subjects_dict[subject_name]['pdfs'].append({
                'name': title,
                'src': url
            })
    
    # Convert to the required format
    result = []
    for subject_name, content in subjects_dict.items():
        if content['videos'] or content['pdfs']:
            result.append({
                'folder': subject_name,
                'subjects': [{
                    'name': subject_name,
                    'videos': content['videos'],
                    'pdfs': content['pdfs']
                }]
            })
    
    return result

def generate_html(data, output_path, user_info=None):
    """Generate HTML file from parsed data with watermark"""
    # Convert data to JSON string for JavaScript
    data_json = json.dumps(data, ensure_ascii=False, indent=2)
    
    # User info for watermark
    user_id = user_info.get('user_id', 'Unknown') if user_info else 'Unknown'
    username = user_info.get('username', 'User') if user_info else 'User'
    first_name = user_info.get('first_name', 'User') if user_info else 'User'
    
    watermark_text = f"{first_name} (ID: {user_id})"
    
    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Engineers Babu | HTML Viewer</title>

<style>
/* ================= THEME VARIABLES ================= */
:root{{
  /* 🌙 DARK THEME */
  --page-bg:#0f1117;
  --card-bg:#161b22;
  --inner-bg:#1f2633;
  --text:#e5e7eb;
  --muted:#9ca3af;
  --border:rgba(255,255,255,0.08);
  --shadow:none;
  --primary:#2563eb;
}}

.light{{
  /* ☀️ LIGHT THEME */
  --page-bg:#f4f6fb;
  --card-bg:#ffffff;
  --inner-bg:#f1f4fb;
  --text:#1f2937;
  --muted:#6b7280;
  --border:rgba(0,0,0,0.06);
  --shadow:0 8px 24px rgba(0,0,0,0.05);
  --primary:#2563eb;
}}

/* ================= BASE ================= */
*{{
  margin:0;
  padding:0;
  box-sizing:border-box;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto;
}}

body{{
  background:var(--page-bg);
  color:var(--text);
  transition:background .3s,color .3s;
  overflow-x:hidden;
}}

/* Disable text selection and right click */
body {{
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}}

/* ================= HEADER ================= */
.main-header{{
  position:relative;
  display:flex;
  justify-content:flex-end;
  align-items:center;
  padding:18px 20px;
  background:var(--card-bg);
  border-bottom:1px solid var(--border);
}}

.title-box{{
  position:absolute;
  left:50%;
  transform:translateX(-50%);
  text-align:center;
}}

.title-box h1{{
  font-size:42px;
  font-weight:800;
  background:linear-gradient(90deg,#00f5ff,#E50914,#ffcc00);
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
  letter-spacing:2px;
}}

.title-box span{{
  font-size:13px;
  color:var(--muted);
  letter-spacing:3px;
}}

.toggle{{
  cursor:pointer;
  padding:8px 14px;
  border-radius:20px;
  background:var(--inner-bg);
  border:1px solid var(--border);
}}

/* ===== GRADIENT LINE ===== */
.gradient-bar{{
  height:6px;
  background:linear-gradient(
    90deg,
    #00f5ff,
    #7a00ff,
    #E50914,
    #ffcc00
  );
}}

/* ================= SEARCH ================= */
.search{{
  padding:14px;
}}

.search input{{
  width:100%;
  padding:12px;
  border-radius:12px;
  border:none;
  outline:none;
  background:var(--card-bg);
  color:var(--text);
  box-shadow:var(--shadow);
}}

/* ================= LAYOUT ================= */
.container{{
  display:grid;
  grid-template-columns:280px 1fr 360px;
  gap:18px;
  padding:18px;
}}

/* ================= CARD ================= */
.card{{
  background:var(--card-bg);
  border-radius:18px;
  padding:14px;
  border:1px solid var(--border);
  box-shadow:var(--shadow);
}}

/* ================= SUBJECTS ================= */
.folder-title{{
  padding:12px;
  border-radius:12px;
  background:var(--inner-bg);
  font-weight:600;
  cursor:pointer;
}}

.subject{{
  margin-top:6px;
  padding:10px;
  border-radius:10px;
  background:var(--inner-bg);
  cursor:pointer;
}}

.subject:hover,
.subject.active{{
  background:var(--primary);
  color:#fff;
}}

/* ================= VIDEO ================= */
#videoPlayer{{
  margin-top:10px;
  background:var(--inner-bg);
  border-radius:14px;
  overflow:hidden;
  position:relative;
}}

.video-container {{
  position:relative;
  width:100%;
  padding-top:56.25%; /* 16:9 Aspect Ratio */
  background:black;
  border-radius:12px;
  overflow:hidden;
}}

.video-iframe {{
  position:absolute;
  top:0;
  left:0;
  width:100%;
  height:100%;
  border:none;
}}

/* Video Watermark */
.video-watermark {{
  position:absolute;
  top:10px;
  right:10px;
  background:rgba(0,0,0,0.7);
  color:#fff;
  padding:5px 12px;
  border-radius:5px;
  font-size:12px;
  z-index:1000;
  pointer-events:none;
  font-weight:600;
}}

.playlist-item{{
  margin-top:6px;
  padding:10px;
  border-radius:10px;
  background:var(--inner-bg);
  cursor:pointer;
}}

.playlist-item:hover,
.playlist-item.active{{
  background:var(--primary);
  color:#fff;
}}

/* ================= PDF ================= */
.pdf-item{{
  margin-bottom:6px;
  padding:10px;
  border-radius:10px;
  background:var(--inner-bg);
  cursor:pointer;
}}

.pdf-item:hover,
.pdf-item.active{{
  background:var(--primary);
  color:#fff;
}}

/* PDF Fullscreen Modal */
.pdf-modal {{
  display:none;
  position:fixed;
  top:0;
  left:0;
  width:100%;
  height:100%;
  background:rgba(0,0,0,0.95);
  z-index:9999;
}}

.pdf-modal.active {{
  display:flex;
  flex-direction:column;
}}

.pdf-modal-header {{
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding:15px 20px;
  background:var(--card-bg);
  border-bottom:1px solid var(--border);
}}

.pdf-modal-title {{
  font-size:16px;
  font-weight:600;
  color:var(--text);
}}

.pdf-close-btn {{
  cursor:pointer;
  padding:8px 16px;
  background:var(--primary);
  color:#fff;
  border:none;
  border-radius:8px;
  font-weight:600;
}}

.pdf-modal-content {{
  flex:1;
  position:relative;
}}

.pdf-modal-iframe {{
  width:100%;
  height:100%;
  border:none;
}}

/* ================= RESPONSIVE ================= */
@media(max-width:900px){{
  .container{{
    grid-template-columns:1fr;
  }}
  
  .title-box h1{{
    font-size:32px;
  }}
  
  .video-container {{
    padding-top:56.25%;
  }}
}}

@media(max-width:600px){{
  .title-box h1{{
    font-size:24px;
  }}
  
  .container{{
    padding:10px;
    gap:10px;
  }}
}}

/* ================= FULLSCREEN SUPPORT ================= */
.fullscreen-video {{
  position:fixed !important;
  top:0 !important;
  left:0 !important;
  width:100% !important;
  height:100% !important;
  z-index:9999 !important;
  padding-top:0 !important;
}}

.fullscreen-video .video-iframe {{
  border-radius:0 !important;
}}
</style>
</head>

<body class="light">

<header class="main-header">
  <div class="title-box">
    <h1>Engineers Babu</h1>
    <span>HTML VIEWER</span>
  </div>
  <div class="toggle" onclick="toggleTheme()">🌙 / ☀️</div>
</header>

<div class="gradient-bar"></div>

<div class="search">
  <input type="text" placeholder="Search subject..." onkeyup="filterSubjects(this.value)">
</div>

<div class="container">

  <!-- LEFT -->
  <div class="card" id="subjects"></div>

  <!-- CENTER -->
  <div class="card" id="videoSection">
    <h3>🎬 Video Player</h3>
    <div id="videoPlayer"></div>
    <div id="playlist"></div>
  </div>

  <!-- RIGHT -->
  <div class="card">
    <h3>📄 PDF Files</h3>
    <div id="pdfList"></div>
  </div>

</div>

<!-- PDF Fullscreen Modal -->
<div class="pdf-modal" id="pdfModal">
  <div class="pdf-modal-header">
    <div class="pdf-modal-title" id="pdfModalTitle">PDF Viewer</div>
    <button class="pdf-close-btn" onclick="closePdfModal()">✕ Close</button>
  </div>
  <div class="pdf-modal-content">
    <iframe class="pdf-modal-iframe" id="pdfModalViewer"></iframe>
  </div>
</div>

<script>
/* ================= DISABLE RIGHT CLICK ================= */
document.addEventListener('contextmenu', function(e) {{
  e.preventDefault();
  return false;
}});

/* Disable F12, Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+U */
document.addEventListener('keydown', function(e) {{
  if (e.keyCode == 123 || // F12
      (e.ctrlKey && e.shiftKey && e.keyCode == 73) || // Ctrl+Shift+I
      (e.ctrlKey && e.shiftKey && e.keyCode == 74) || // Ctrl+Shift+J
      (e.ctrlKey && e.keyCode == 85)) {{ // Ctrl+U
    e.preventDefault();
    return false;
  }}
}});

/* ================= THEME TOGGLE ================= */
function toggleTheme(){{
  document.body.classList.toggle("light");
}}

/* ================= DATA ================= */
const data = {data_json};
const userWatermark = "{watermark_text}";

/* ================= SCREEN ORIENTATION ================= */
function lockOrientation() {{
  if (screen.orientation && screen.orientation.lock) {{
    screen.orientation.lock('landscape').catch(err => {{
      console.log('Orientation lock not supported');
    }});
  }}
}}

/* ================= PDF MODAL ================= */
function openPdfModal(pdfUrl, pdfName) {{
  const modal = document.getElementById('pdfModal');
  const iframe = document.getElementById('pdfModalViewer');
  const title = document.getElementById('pdfModalTitle');
  
  title.textContent = pdfName;
  iframe.src = pdfUrl;
  modal.classList.add('active');
  
  // Lock orientation on mobile
  lockOrientation();
}}

function closePdfModal() {{
  const modal = document.getElementById('pdfModal');
  const iframe = document.getElementById('pdfModalViewer');
  
  iframe.src = '';
  modal.classList.remove('active');
}}

/* Close modal on escape key */
document.addEventListener('keydown', function(e) {{
  if (e.key === 'Escape') {{
    closePdfModal();
  }}
}});

/* ================= LOGIC ================= */
function renderSubjects(){{
  let html="";
  data.forEach(f=>{{
    html+=`
      <div class="folder-title"
        onclick="this.nextElementSibling.style.display =
        this.nextElementSibling.style.display==='block'?'none':'block'">
        📁 ${{f.folder}}
      </div>
      <div style="display:none;padding-left:6px;">
    `;
    f.subjects.forEach(s=>{{
      html+=`<div class="subject" onclick='loadSubject(${{JSON.stringify(s)}},this)'>${{s.name}}</div>`;
    }});
    html+=`</div>`;
  }});
  subjects.innerHTML=html;
}}

function loadSubject(sub,el){{
  document.querySelectorAll(".subject").forEach(x=>x.classList.remove("active"));
  el.classList.add("active");
  
  if(sub.videos && sub.videos.length > 0){{
    playVideo(sub.videos[0]);
    renderPlaylist(sub.videos);
    
    // Scroll to video section
    document.getElementById('videoSection').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
  }} else {{
    videoPlayer.innerHTML="<p style='padding:20px;text-align:center;color:var(--muted)'>No videos available</p>";
    playlist.innerHTML="";
  }}
  
  if(sub.pdfs && sub.pdfs.length > 0){{
    renderPdf(sub.pdfs);
  }} else {{
    pdfList.innerHTML="<p style='padding:10px;text-align:center;color:var(--muted)'>No PDFs available</p>";
  }}
}}

function playVideo(v){{
  videoPlayer.innerHTML="";
  
  // Create video container with watermark
  const videoHTML = `
    <div class="video-container" id="videoContainer">
      <div class="video-watermark">${{userWatermark}}</div>
      <iframe class="video-iframe" 
              id="videoIframe" 
              src="${{v.src}}" 
              allowfullscreen
              allow="autoplay; encrypted-media; picture-in-picture; fullscreen">
      </iframe>
    </div>
  `;
  
  videoPlayer.innerHTML = videoHTML;
  
  // Scroll to video
  document.getElementById('videoSection').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
  
  // Lock orientation on mobile
  lockOrientation();
  
  // Handle fullscreen
  const videoContainer = document.getElementById('videoContainer');
  const videoIframe = document.getElementById('videoIframe');
  
  videoIframe.addEventListener('dblclick', function() {{
    if (!document.fullscreenElement) {{
      videoContainer.requestFullscreen().catch(err => {{
        console.log('Fullscreen not supported');
      }});
    }}
  }});
}}

function renderPlaylist(vs){{
  playlist.innerHTML=vs.map((v, idx)=>
    `<div class="playlist-item" onclick='playVideo(${{JSON.stringify(v)}});highlightPlaylistItem(this)' data-idx="${{idx}}">${{v.title}}</div>`
  ).join("");
}}

function highlightPlaylistItem(el){{
  document.querySelectorAll(".playlist-item").forEach(x=>x.classList.remove("active"));
  el.classList.add("active");
}}

function renderPdf(p){{
  pdfList.innerHTML=p.map((x, idx)=>
    `<div class="pdf-item" onclick="openPdfModal('${{x.src}}', '${{x.name.replace(/'/g, "\\\\'")}}');highlightPdfItem(this)" data-idx="${{idx}}">${{x.name}}</div>`
  ).join("");
}}

function highlightPdfItem(el){{
  document.querySelectorAll(".pdf-item").forEach(x=>x.classList.remove("active"));
  el.classList.add("active");
}}

function filterSubjects(val){{
  document.querySelectorAll(".subject").forEach(s=>{{
    s.style.display = s.innerText.toLowerCase().includes(val.toLowerCase())
      ? "block" : "none";
  }});
}}

/* ================= INITIALIZE ================= */
renderSubjects();

/* Auto-open first folder */
setTimeout(() => {{
  const firstFolder = document.querySelector('.folder-title');
  if (firstFolder) {{
    firstFolder.click();
  }}
}}, 500);
</script>

</body>
</html>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    return output_path

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    await update.message.reply_text(
        "👋 Welcome to Engineers Babu HTML Generator Bot!\n\n"
        "📤 Send me a .txt file with the format:\n"
        "(Category)Title:URL\n\n"
        "I'll generate an HTML viewer for you! 🚀"
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle uploaded document"""
    document = update.message.document
    user = update.message.from_user
    
    # Check if it's a txt file
    if not document.file_name.endswith('.txt'):
        await update.message.reply_text("❌ Please send a .txt file!")
        return
    
    await update.message.reply_text("⏳ Processing your file...")
    
    try:
        # Download file
        file = await context.bot.get_file(document.file_id)
        input_path = f"/tmp/{document.file_name}"
        await file.download_to_drive(input_path)
        
        # Parse the file
        parsed_data = parse_txt_file(input_path)
        
        # User info for watermark
        user_info = {
            'user_id': user.id,
            'username': user.username or 'user',
            'first_name': user.first_name or 'User'
        }
        
        # Generate HTML
        output_filename = document.file_name.replace('.txt', '.html')
        output_path = f"/tmp/{output_filename}"
        generate_html(parsed_data, output_path, user_info)
        
        # Send the generated HTML file
        with open(output_path, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=output_filename,
                caption=f"✅ HTML file generated successfully!\n\n"
                        f"📊 Found {len(parsed_data)} subjects\n"
                        f"🎬 Ready to view your videos and PDFs!\n"
                        f"👤 Personalized for: {user.first_name} (ID: {user.id})"
            )
        
        # Clean up
        os.remove(input_path)
        os.remove(output_path)
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        await update.message.reply_text(f"❌ Error processing file: {str(e)}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Start the bot"""
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ Please set BOT_TOKEN environment variable")
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("🤖 Bot started! Send /start to begin.")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()
import os
import threading
from fastapi import FastAPI
import uvicorn

PORT = int(os.environ.get("PORT", 10000))

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}

def run_bot():
    # YOUR existing telegram bot code
    # application.run_polling()
    pass

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=PORT)
