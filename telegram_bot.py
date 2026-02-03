import os
import re
import json
import urllib.parse
import logging
from difflib import SequenceMatcher
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

def normalize_title(title):
    """
    Normalize title for better matching
    Removes common suffixes like 'Notes', 'PDF', 'Solution', etc.
    """
    # Convert to lowercase for comparison
    normalized = title.lower()
    
    # Remove common suffixes
    suffixes_to_remove = [
        r'\s*notes?\s*',
        r'\s*pdf\s*',
        r'\s*solutions?\s*',
        r'\s*handouts?\s*',
        r'\s*worksheet\s*',
        r'\s*practice\s*',
        r'\s*assignment\s*',
        r'\s*quiz\s*',
        r'\s*exam\s*',
        r'\s*test\s*',
        r'\s*question\s*',
        r'\s*answer\s*',
        r'\s*book\s*',
        r'\s*material\s*',
        r'\s*document\s*',
        r'\s*file\s*',
    ]
    
    for suffix in suffixes_to_remove:
        normalized = re.sub(suffix + r'$', '', normalized, flags=re.IGNORECASE)
    
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    # Remove special characters for better matching
    normalized = re.sub(r'[^\w\s-]', '', normalized)
    
    return normalized

def calculate_similarity(str1, str2):
    """
    Calculate similarity between two strings
    Returns a value between 0 and 1 (1 = identical)
    """
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

def extract_lecture_info(title):
    """
    Extract lecture number and core topic from title
    Examples:
    - "Lect-1 Basic of Networks" -> (1, "Basic of Networks")
    - "Lect.-2 Physics Chapter 1" -> (2, "Physics Chapter 1")
    - "Lecture 3 Mathematics" -> (3, "Mathematics")
    """
    # Try different lecture formats
    patterns = [
        r'(?:lect|lecture)[.-]?\s*(\d+)\s+(.+)',  # Lect-1, Lect.-1, Lecture 1
        r'(?:class|session)[.-]?\s*(\d+)\s+(.+)',  # Class-1, Session 1
        r'(?:ch|chapter)[.-]?\s*(\d+)\s+(.+)',     # Ch-1, Chapter 1
    ]
    
    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            lecture_num = int(match.group(1))
            topic = match.group(2).strip()
            # Remove parenthetical content
            topic = re.sub(r'\([^)]*\)', '', topic).strip()
            return (lecture_num, topic)
    
    return (None, title)

def find_matching_group(title, existing_groups, threshold=0.7):
    """
    Find which existing group this title belongs to
    Uses intelligent name matching
    """
    normalized_title = normalize_title(title)
    lecture_num, topic = extract_lecture_info(title)
    
    best_match = None
    best_score = 0
    
    for group_name, group_data in existing_groups.items():
        # Get the normalized group name
        normalized_group = normalize_title(group_name)
        
        # Calculate similarity
        similarity = calculate_similarity(normalized_title, normalized_group)
        
        # If we have lecture numbers, check if they match
        if lecture_num is not None and 'lecture_num' in group_data:
            if lecture_num == group_data['lecture_num']:
                # Same lecture number boosts the score
                similarity += 0.2
        
        # Check if the core topic matches
        if topic:
            group_topic = group_data.get('topic', '')
            if group_topic:
                topic_similarity = calculate_similarity(
                    normalize_title(topic),
                    normalize_title(group_topic)
                )
                # Topic similarity is very important
                similarity = (similarity + topic_similarity * 2) / 3
        
        # Update best match if this is better
        if similarity > best_score and similarity >= threshold:
            best_score = similarity
            best_match = group_name
    
    return best_match, best_score

def parse_txt_file(file_path):
    """
    Parse the txt file and intelligently classify subjects with videos and PDFs
    Uses smart name matching to group related content together
    
    Supports BOTH formats:
    1. (Category)Title:URL
    2. Title: URL (without category)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # First pass: collect all items
    all_items = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Skip HTML content
        if line.startswith('<') or line.startswith('<!'):
            continue
            
        category = None
        title = None
        url = None
        
        # Try format 1: (Category)Title:URL
        match = re.match(r'\(([^)]+)\)(.+?):(https?://.+)', line)
        if match:
            category = match.group(1).strip()
            title = match.group(2).strip()
            url = match.group(3).strip()
        else:
            # Try format 2: Title: URL (without category)
            match = re.match(r'(.+?):\s*(https?://.+)', line)
            if match:
                title = match.group(1).strip()
                url = match.group(2).strip()
                category = "General"
        
        # Skip if we couldn't parse the line
        if not title or not url:
            continue
        
        # Determine if it's video or PDF
        is_pdf = url.lower().endswith('.pdf')
        is_video = not is_pdf
        
        # Extract lecture info
        lecture_num, topic = extract_lecture_info(title)
        
        all_items.append({
            'title': title,
            'url': url,
            'category': category,
            'is_pdf': is_pdf,
            'is_video': is_video,
            'lecture_num': lecture_num,
            'topic': topic,
            'normalized_title': normalize_title(title)
        })
    
    # Second pass: intelligent grouping
    subjects_dict = {}
    
    for item in all_items:
        # Try to find matching group
        matching_group, similarity = find_matching_group(
            item['title'],
            subjects_dict,
            threshold=0.65  # Lower threshold for better grouping
        )
        
        if matching_group:
            # Add to existing group
            subject_name = matching_group
        else:
            # Create new group
            # Use the topic as the subject name, or full title if no topic
            if item['topic'] and len(item['topic']) > 3:
                subject_name = item['topic']
            else:
                subject_name = item['title'] if len(item['title']) < 50 else item['title'][:50] + "..."
            
            # Initialize new group
            subjects_dict[subject_name] = {
                'videos': [],
                'pdfs': [],
                'lecture_num': item['lecture_num'],
                'topic': item['topic']
            }
        
        # Process Classplus URLs through API
        url = item['url']
        if item['is_video'] and 'classplus' in url.lower():
            url = f"https://engineers-babu.onrender.com/?url={urllib.parse.quote(url)}"
        
        # Add to appropriate list
        if item['is_video']:
            subjects_dict[subject_name]['videos'].append({
                'title': item['title'],
                'src': url,
                'drm': 'classplus' in item['url'].lower()
            })
        else:
            subjects_dict[subject_name]['pdfs'].append({
                'name': item['title'],
                'src': url
            })
    
    # Third pass: merge similar groups (post-processing)
    merged_subjects = {}
    processed_keys = set()
    
    for subject_name in subjects_dict.keys():
        if subject_name in processed_keys:
            continue
        
        # Find all similar subjects
        similar_subjects = [subject_name]
        for other_subject in subjects_dict.keys():
            if other_subject == subject_name or other_subject in processed_keys:
                continue
            
            similarity = calculate_similarity(
                normalize_title(subject_name),
                normalize_title(other_subject)
            )
            
            if similarity >= 0.85:  # High threshold for merging
                similar_subjects.append(other_subject)
                processed_keys.add(other_subject)
        
        # Merge all similar subjects
        merged_videos = []
        merged_pdfs = []
        
        for subj in similar_subjects:
            merged_videos.extend(subjects_dict[subj]['videos'])
            merged_pdfs.extend(subjects_dict[subj]['pdfs'])
        
        # Use the shortest name as the merged name
        merged_name = min(similar_subjects, key=len)
        
        merged_subjects[merged_name] = {
            'videos': merged_videos,
            'pdfs': merged_pdfs
        }
        processed_keys.add(subject_name)
    
    # Convert to the required format
    result = []
    for subject_name, content in merged_subjects.items():
        if content['videos'] or content['pdfs']:
            result.append({
                'folder': subject_name,
                'subjects': [{
                    'name': subject_name,
                    'videos': content['videos'],
                    'pdfs': content['pdfs']
                }]
            })
    
    # Sort by subject name for better organization
    result.sort(key=lambda x: x['folder'])
    
    return result

def generate_html(data, output_path):
    """Generate HTML file from parsed data with enhanced PDF viewer"""
    # Convert data to JSON string for JavaScript
    data_json = json.dumps(data, ensure_ascii=False, indent=2)
    
    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Engineers Babu | Smart HTML Viewer</title>

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
  --inner-bg:#f8f9fa;
  --text:#1f2937;
  --muted:#6b7280;
  --border:#e5e7eb;
  --shadow:0 1px 3px rgba(0,0,0,0.1);
  --primary:#3b82f6;
}}

/* ================= RESET & BASE ================= */
*{{margin:0;padding:0;box-sizing:border-box}}
body{{
  font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  background:var(--page-bg);
  color:var(--text);
  line-height:1.6;
  transition:background 0.3s;
}}

/* ================= HEADER ================= */
header{{
  background:var(--card-bg);
  border-bottom:1px solid var(--border);
  padding:15px 0;
  position:sticky;
  top:0;
  z-index:100;
  box-shadow:var(--shadow);
}}

.container{{max-width:1200px;margin:0 auto;padding:0 20px}}

.header-content{{
  display:flex;
  justify-content:space-between;
  align-items:center;
  flex-wrap:wrap;
  gap:15px;
}}

h1{{
  font-size:1.5rem;
  font-weight:700;
  background:linear-gradient(135deg,#667eea,#764ba2);
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
  background-clip:text;
}}

.controls{{
  display:flex;
  gap:10px;
  align-items:center;
}}

.search-box{{
  padding:8px 15px;
  border:1px solid var(--border);
  border-radius:8px;
  background:var(--inner-bg);
  color:var(--text);
  outline:none;
  min-width:200px;
  transition:border-color 0.3s;
}}

.search-box:focus{{border-color:var(--primary)}}

.theme-toggle{{
  background:var(--inner-bg);
  border:1px solid var(--border);
  color:var(--text);
  padding:8px 15px;
  border-radius:8px;
  cursor:pointer;
  font-size:14px;
  transition:all 0.3s;
}}

.theme-toggle:hover{{
  background:var(--primary);
  color:white;
  border-color:var(--primary);
}}

/* ================= MAIN LAYOUT ================= */
.main-layout{{
  display:grid;
  grid-template-columns:300px 1fr;
  gap:20px;
  padding:20px;
  max-width:1400px;
  margin:0 auto;
}}

/* ================= SIDEBAR ================= */
.sidebar{{
  background:var(--card-bg);
  border-radius:12px;
  padding:20px;
  border:1px solid var(--border);
  max-height:calc(100vh - 120px);
  overflow-y:auto;
  position:sticky;
  top:100px;
}}

.folder{{margin-bottom:15px}}

.folder-header{{
  padding:10px;
  background:var(--inner-bg);
  border-radius:8px;
  cursor:pointer;
  font-weight:600;
  display:flex;
  justify-content:space-between;
  align-items:center;
  transition:all 0.3s;
  border:1px solid transparent;
}}

.folder-header:hover{{
  background:var(--primary);
  color:white;
  border-color:var(--primary);
}}

.folder-header.active{{
  background:var(--primary);
  color:white;
}}

.subject-item{{
  padding:8px 15px;
  margin:5px 0 5px 15px;
  border-left:2px solid var(--border);
  cursor:pointer;
  transition:all 0.3s;
  border-radius:4px;
}}

.subject-item:hover{{
  background:var(--inner-bg);
  border-left-color:var(--primary);
  padding-left:20px;
}}

.subject-item.active{{
  background:var(--primary);
  color:white;
  border-left-color:white;
}}

/* ================= CONTENT AREA ================= */
.content-area{{
  background:var(--card-bg);
  border-radius:12px;
  padding:25px;
  border:1px solid var(--border);
  min-height:500px;
}}

.subject-title{{
  font-size:1.8rem;
  margin-bottom:20px;
  padding-bottom:15px;
  border-bottom:2px solid var(--border);
  color:var(--text);
}}

.section{{margin-bottom:30px}}

.section-title{{
  font-size:1.2rem;
  margin-bottom:15px;
  color:var(--muted);
  font-weight:600;
}}

/* ================= VIDEO SECTION ================= */
.video-player{{
  background:#000;
  border-radius:12px;
  overflow:hidden;
  margin-bottom:20px;
  box-shadow:0 4px 6px rgba(0,0,0,0.3);
}}

video{{
  width:100%;
  height:auto;
  display:block;
  max-height:500px;
}}

.playlist{{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(280px,1fr));
  gap:12px;
  margin-top:15px;
}}

.playlist-item{{
  padding:12px 15px;
  background:var(--inner-bg);
  border-radius:8px;
  cursor:pointer;
  transition:all 0.3s;
  border:2px solid transparent;
  display:flex;
  align-items:center;
  gap:10px;
}}

.playlist-item:hover{{
  background:var(--primary);
  color:white;
  transform:translateY(-2px);
  box-shadow:0 4px 8px rgba(0,0,0,0.2);
}}

.playlist-item.active{{
  border-color:var(--primary);
  background:var(--primary);
  color:white;
}}

.play-icon{{
  width:30px;
  height:30px;
  background:var(--primary);
  border-radius:50%;
  display:flex;
  align-items:center;
  justify-content:center;
  color:white;
  flex-shrink:0;
}}

.playlist-item.active .play-icon,
.playlist-item:hover .play-icon{{
  background:white;
  color:var(--primary);
}}

/* ================= PDF SECTION ================= */
.pdf-container{{
  background:var(--inner-bg);
  border-radius:12px;
  padding:15px;
  display:grid;
  grid-template-columns:200px 1fr;
  gap:15px;
  min-height:600px;
}}

.pdf-list{{
  display:flex;
  flex-direction:column;
  gap:8px;
  max-height:600px;
  overflow-y:auto;
  padding-right:10px;
}}

.pdf-item{{
  padding:10px 12px;
  background:var(--card-bg);
  border-radius:6px;
  cursor:pointer;
  transition:all 0.3s;
  border:1px solid transparent;
  font-size:14px;
}}

.pdf-item:hover{{
  background:var(--primary);
  color:white;
  transform:translateX(5px);
}}

.pdf-item.active{{
  background:var(--primary);
  color:white;
  border-color:white;
}}

.pdf-viewer-container{{
  background:white;
  border-radius:8px;
  overflow:hidden;
  position:relative;
}}

.pdf-controls{{
  display:flex;
  gap:10px;
  padding:10px;
  background:var(--card-bg);
  border-bottom:1px solid var(--border);
  justify-content:center;
}}

.pdf-controls button{{
  padding:8px 16px;
  background:var(--primary);
  color:white;
  border:none;
  border-radius:6px;
  cursor:pointer;
  font-size:14px;
  transition:all 0.3s;
}}

.pdf-controls button:hover{{
  background:#1e40af;
  transform:translateY(-2px);
}}

iframe{{
  width:100%;
  height:550px;
  border:none;
  background:white;
}}

/* ================= RESPONSIVE ================= */
@media(max-width:768px){{
  .main-layout{{
    grid-template-columns:1fr;
  }}
  .sidebar{{
    position:static;
    max-height:none;
  }}
  .pdf-container{{
    grid-template-columns:1fr;
  }}
  .pdf-list{{
    max-height:300px;
  }}
}}

/* ================= SCROLLBAR ================= */
::-webkit-scrollbar{{width:8px;height:8px}}
::-webkit-scrollbar-track{{background:var(--inner-bg)}}
::-webkit-scrollbar-thumb{{background:var(--muted);border-radius:4px}}
::-webkit-scrollbar-thumb:hover{{background:var(--primary)}}

/* ================= EMPTY STATE ================= */
.empty-state{{
  text-align:center;
  padding:60px 20px;
  color:var(--muted);
}}

.empty-state h3{{
  font-size:1.5rem;
  margin-bottom:10px;
}}
</style>

<!-- Shaka Player for DRM content -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/shaka-player/4.3.5/shaka-player.compiled.min.js"></script>
</head>
<body>

<!-- ================= HEADER ================= -->
<header>
  <div class="container">
    <div class="header-content">
      <h1>ðŸ"š Engineers Babu | Smart Viewer</h1>
      <div class="controls">
        <input type="text" class="search-box" id="searchBox" placeholder="ðŸ" Search subjects...">
        <button class="theme-toggle" onclick="toggleTheme()">ðŸŒ™ Dark/Light</button>
      </div>
    </div>
  </div>
</header>

<!-- ================= MAIN LAYOUT ================= -->
<div class="main-layout">
  
  <!-- SIDEBAR -->
  <aside class="sidebar" id="sidebar">
    <!-- Subjects will be rendered here -->
  </aside>

  <!-- CONTENT AREA -->
  <main class="content-area" id="contentArea">
    <div class="empty-state">
      <h3>👋 Welcome!</h3>
      <p>Select a subject from the sidebar to begin</p>
    </div>
  </main>

</div>

<script>
// ================= DATA ================= 
const DATA = {data_json};

// ================= STATE =================
let currentSubject = null;
let currentVideo = null;
let currentPdfUrl = null;
let player = null;

// ================= THEME =================
function toggleTheme() {{
  document.body.classList.toggle('light');
  localStorage.setItem('theme', document.body.classList.contains('light') ? 'light' : 'dark');
}}

// Load saved theme
if (localStorage.getItem('theme') === 'light') {{
  document.body.classList.add('light');
}}

// ================= RENDER SIDEBAR =================
function renderSidebar(filterText = '') {{
  const sidebar = document.getElementById('sidebar');
  const filtered = DATA.filter(folder => 
    folder.folder.toLowerCase().includes(filterText.toLowerCase())
  );
  
  sidebar.innerHTML = filtered.map((folder, fidx) => `
    <div class="folder">
      <div class="folder-header" onclick="toggleFolder(${{fidx}})">
        ${{folder.folder}}
        <span>▼</span>
      </div>
      <div id="folder-${{fidx}}" style="display:block">
        ${{folder.subjects.map((subj, sidx) => `
          <div class="subject-item" onclick="loadSubject(${{fidx}}, ${{sidx}})">
            ${{subj.name}}
          </div>
        `).join('')}}
      </div>
    </div>
  `).join('');
}}

// ================= TOGGLE FOLDER =================
function toggleFolder(fidx) {{
  const folder = document.getElementById(`folder-${{fidx}}`);
  folder.style.display = folder.style.display === 'none' ? 'block' : 'none';
}}

// ================= LOAD SUBJECT =================
function loadSubject(fidx, sidx) {{
  currentSubject = DATA[fidx].subjects[sidx];
  
  // Highlight active subject
  document.querySelectorAll('.subject-item').forEach(el => el.classList.remove('active'));
  event.target.classList.add('active');
  
  renderContent();
}}

// ================= RENDER CONTENT =================
function renderContent() {{
  const content = document.getElementById('contentArea');
  if (!currentSubject) return;
  
  content.innerHTML = `
    <h2 class="subject-title">${{currentSubject.name}}</h2>
    
    ${{currentSubject.videos && currentSubject.videos.length > 0 ? `
      <div class="section">
        <div class="section-title">ðŸŽ¬ Videos (${{currentSubject.videos.length}})</div>
        <div class="video-player">
          <video id="videoPlayer" controls></video>
        </div>
        <div class="playlist" id="playlist"></div>
      </div>
    ` : ''}}
    
    ${{currentSubject.pdfs && currentSubject.pdfs.length > 0 ? `
      <div class="section">
        <div class="section-title">ðŸ"„ PDFs (${{currentSubject.pdfs.length}})</div>
        <div class="pdf-container">
          <div class="pdf-list" id="pdfList"></div>
          <div class="pdf-viewer-container">
            <div class="pdf-controls" style="display:none;" id="pdfControls">
              <button onclick="openPdfDirect()">ðŸ"¥ Download PDF</button>
              <button onclick="openPdfNewTab()">ðŸ"— Open in New Tab</button>
            </div>
            <iframe id="pdfViewer"></iframe>
          </div>
        </div>
      </div>
    ` : ''}}
  `;
  
  if (currentSubject.videos && currentSubject.videos.length > 0) {{
    renderPlaylist(currentSubject.videos);
    loadVideo(currentSubject.videos[0], 0);
  }}
  
  if (currentSubject.pdfs && currentSubject.pdfs.length > 0) {{
    renderPdfList(currentSubject.pdfs);
  }}
}}

// ================= VIDEO PLAYER =================
function renderPlaylist(videos) {{
  const playlist = document.getElementById('playlist');
  playlist.innerHTML = videos.map((v, idx) => `
    <div class="playlist-item ${{idx === 0 ? 'active' : ''}}" onclick="loadVideo(currentSubject.videos[${{idx}}], ${{idx}})">
      <div class="play-icon">â–¶</div>
      <div>${{v.title}}</div>
    </div>
  `).join('');
}}

function loadVideo(video, idx) {{
  currentVideo = video;
  const videoPlayer = document.getElementById('videoPlayer');
  
  // Highlight active
  document.querySelectorAll('.playlist-item').forEach((el, i) => {{
    el.classList.toggle('active', i === idx);
  }});
  
  if (video.drm) {{
    // Use Shaka Player for DRM
    if (!player) {{
      player = new shaka.Player(videoPlayer);
    }}
    player.load(video.src).catch(e => console.error('Error loading DRM video:', e));
  }} else {{
    // Regular video
    if (player) {{
      player.destroy();
      player = null;
    }}
    videoPlayer.src = video.src;
  }}
  
  videoPlayer.play();
}}

// ================= PDF VIEWER =================
function renderPdfList(pdfs) {{
  const pdfList = document.getElementById('pdfList');
  pdfList.innerHTML = pdfs.map((p, idx) => `
    <div class="pdf-item ${{idx === 0 ? 'active' : ''}}" onclick="loadPdf('${{p.src}}', '${{p.name}}', ${{idx}})">
      ${{p.name}}
    </div>
  `).join('');
  
  if (pdfs.length > 0) {{
    loadPdf(pdfs[0].src, pdfs[0].name, 0);
  }}
}}

function loadPdf(url, name, idx) {{
  currentPdfUrl = url;
  const pdfViewer = document.getElementById('pdfViewer');
  const pdfControls = document.getElementById('pdfControls');
  
  // Highlight active
  document.querySelectorAll('.pdf-item').forEach((el, i) => {{
    el.classList.toggle('active', i === idx);
  }});
  
  // Method 1: Google Docs Viewer (Primary - handles CORS)
  const googleDocsUrl = `https://docs.google.com/viewer?url=${{encodeURIComponent(url)}}&embedded=true`;
  
  // Method 2: PDF.js Viewer (Fallback)
  const pdfJsUrl = `https://mozilla.github.io/pdf.js/web/viewer.html?file=${{encodeURIComponent(url)}}`;
  
  // Try Google Docs first
  pdfViewer.src = googleDocsUrl;
  pdfControls.style.display = "flex";
  
  // Fallback to PDF.js if Google Docs fails
  pdfViewer.onerror = function() {{
    console.log("Google Docs viewer failed, trying PDF.js...");
    pdfViewer.src = pdfJsUrl;
  }};
  
  // Smart fallback with timeout
  setTimeout(() => {{
    try {{
      if (!pdfViewer.contentWindow || !pdfViewer.contentWindow.document.body) {{
        console.log("Switching to PDF.js viewer...");
        pdfViewer.src = pdfJsUrl;
      }}
    }} catch(e) {{
      // Cross-origin error is expected and normal
      console.log("PDF loading (cross-origin restriction normal)");
    }}
  }}, 3000);
}}

function openPdfDirect() {{
  if (currentPdfUrl) {{
    const a = document.createElement('a');
    a.href = currentPdfUrl;
    a.download = 'document.pdf';
    a.click();
  }}
}}

function openPdfNewTab() {{
  if (currentPdfUrl) {{
    window.open(currentPdfUrl, '_blank');
  }}
}}

// ================= SEARCH =================
document.getElementById('searchBox').addEventListener('input', (e) => {{
  renderSidebar(e.target.value);
}});

// ================= INITIALIZE =================
renderSidebar();

// Auto-load first subject if available
if (DATA.length > 0 && DATA[0].subjects.length > 0) {{
  setTimeout(() => loadSubject(0, 0), 100);
}}
</script>

</body>
</html>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    return output_path

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_message = """
👋 Welcome to Engineers Babu Smart HTML Generator Bot!

🎯 **NEW! Intelligent Grouping Feature**

This bot now uses **AI-powered name matching** to automatically group related videos and PDFs together!

📤 **How it works:**
1. Send me a .txt file with links
2. Bot analyzes names intelligently
3. Groups videos with their PDFs automatically
4. Creates organized HTML viewer

📋 **Supported formats:**
- `(Category)Title:URL`
- `Title: URL`

✨ **Smart Features:**
- Matches "Lect-1 Physics" with "Lect-1 Physics Notes"
- Groups by lecture number and topic
- Removes duplicates automatically
- Works even if video and PDF are far apart in file

🚀 Send me a .txt file to try it out!
"""
    await update.message.reply_text(welcome_message)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document uploads"""
    document = update.message.document
    
    # Check if it's a txt file
    if not document.file_name.endswith('.txt'):
        await update.message.reply_text("❌ Please send a .txt file only!")
        return
    
    try:
        # Send processing message
        processing_msg = await update.message.reply_text("⏳ Processing your file with smart grouping...")
        
        # Download the file
        file = await context.bot.get_file(document.file_id)
        file_path = f"/tmp/{document.file_name}"
        await file.download_to_drive(file_path)
        
        # Parse the file
        await processing_msg.edit_text("🔍 Analyzing and intelligently grouping content...")
        data = parse_txt_file(file_path)
        
        # Generate statistics
        total_subjects = len(data)
        total_videos = sum(len(s['videos']) for folder in data for s in folder['subjects'])
        total_pdfs = sum(len(s['pdfs']) for folder in data for s in folder['subjects'])
        
        # Generate HTML
        await processing_msg.edit_text("🎨 Generating HTML file...")
        output_file = f"/tmp/{document.file_name.replace('.txt', '.html')}"
        generate_html(data, output_file)
        
        # Send the HTML file
        await processing_msg.edit_text("📤 Sending your HTML file...")
        
        caption = f"""
✅ **File processed successfully!**

📊 **Statistics:**
- 📁 Subjects: {total_subjects}
- 🎬 Videos: {total_videos}
- 📄 PDFs: {total_pdfs}

✨ **Smart grouping applied!**
Related videos and PDFs are automatically grouped together.

🌐 Open the HTML file in your browser!
"""
        
        with open(output_file, 'rb') as f:
            await update.message.reply_document(
                document=f,
                caption=caption,
                filename=document.file_name.replace('.txt', '.html')
            )
        
        # Clean up
        os.remove(file_path)
        os.remove(output_file)
        await processing_msg.delete()
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        await update.message.reply_text(f"❌ Error processing file: {str(e)}")

def main():
    """Start the bot."""
    # Validate token
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Please set BOT_TOKEN environment variable!")
        print("Get your token from @BotFather on Telegram")
        return
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Start the Bot
    print("🤖 Bot started successfully!")
    print("📱 Telegram bot is now polling for messages...")
    print("💡 Send /start to your bot to begin")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
