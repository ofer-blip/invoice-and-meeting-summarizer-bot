import os
import sys
import time
import datetime
import webbrowser
import mimetypes
from google import genai
from google.genai import types
import config

SUMMARIES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'summaries')

PROMPT_MEETING_SUMMARY = """
אתה עוזר מקצועי לניהול, תמלול וסיכום פגישות עסקיות, פדגוגיות ואסטרטגיות בעברית.
האזן היטב לקובץ השמע המצורף של הפגישה/השיחה, והפק סיכום מקיף, תכליתי ומסודר היטב בעברית טבעית ורהוטה.

חשוב מאוד:
1. הקפד על חלוקה מרווחת וקריאה, שבה כל נושא, החלטה ותובנה מופיעים בשורה נפרדת (ולא כגוש טקסט רציף).
2. סווג את הפגישה במדויק בשדה הקטגוריה: 'עסקים' או 'גפ"ן'.

אנא בנה את הסיכום לפי המבנה המדויק הבא:

# סיכום פגישה: [נושא הפגישה המרכזי]

**תאריך ושעה:** [תאריך ושעת הפגישה]
**קטגוריה:** [עסקים / גפ"ן]
**משתתפים/דוברים שזוהו:** [שמות הדוברים או תפקידים שזוהו במהלך השיחה]
**נושא מרכזי:** [משפט אחד שמסביר את מהות הפגישה]

---

## 1. תקציר מנהלים (Executive Summary)
[2-3 פסקאות קצרות וממוקדות שמסבירות את הרקע, הצורך והכיוונים המרכזיים].

## 2. נקודות מפתח ונושאים שנדונו
(הקפד לרשום כל נושא כנקודה נפרדת בשורה משלו עם כותרת מודגשת):
* **[נושא 1]:** [פירוט תמציתי של מה שנדון, עמדות הצדדים ומשמעויות]
* **[נושא 2]:** [פירוט תמציתי של מה שנדון, עמדות הצדדים ומשמעויות]
* **[נושא 3]:** [פירוט תמציתי של מה שנדון, עמדות הצדדים ומשמעויות]

## 3. החלטות שהתקבלו
(רשימה ממוספרת שבה כל החלטה מופיעה בשורה נפרדת לחלוטין ללא טקסט רציף):
1. **[החלטה ראשונה]:** [פירוט קצר של מה שהוחלט וסוכם]
2. **[החלטה שנייה]:** [פירוט קצר של מה שהוחלט וסוכם]
3. **[החלטה שלישית]:** [פירוט קצר של מה שהוחלט וסוכם]

## 4. משימות לביצוע ותוכנית פעולה (Action Items)
- [ ] **משימה 1:** [תיאור המשימה] | **אחראי:** [שם/תפקיד] | **יעד:** [אם מוזכר]
- [ ] **משימה 2:** [תיאור המשימה] | **אחראי:** [שם/תפקיד] | **יעד:** [אם מוזכר]

## 5. תובנות ודגשים להמשך
(הקפד שכל תובנה תהיה בנקודה נפרדת בשורה משלה):
* **[תובנה 1]:** [דגש, הזדמנות או נושא למעקב]
* **[תובנה 2]:** [דגש, הזדמנות או נושא למעקב]

---
*הערה: שמור על עברית טבעית, מקצועית וברורה, תוך שמירה על הקשר מדויק וריווח מלא בין פסקאות.*
"""

def get_mime_type(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    file_name_lower = os.path.basename(file_path).lower()
    
    # WhatsApp and voice recording files often have .mp4 extension but are purely audio
    if ext == '.mp4' and any(k in file_name_lower for k in ['audio', 'voice', 'recording', 'whatsapp', 'ptt', 'קול', 'הקלטה', 'שמע']):
        return 'audio/mp4'
        
    mime_types = {
        '.m4a': 'audio/mp4',
        '.mp3': 'audio/mp3',
        '.wav': 'audio/wav',
        '.aac': 'audio/aac',
        '.ogg': 'audio/ogg',
        '.opus': 'audio/ogg',
        '.flac': 'audio/flac',
        '.webm': 'audio/webm',
        '.mp4': 'video/mp4',
        '.mov': 'video/quicktime',
        '.mkv': 'video/x-matroska',
        '.wma': 'audio/x-ms-wma'
    }
    return mime_types.get(ext, mimetypes.guess_type(file_path)[0] or 'audio/mp4')

def generate_html_summary(md_content, title, source_filename):
    import re
    
    html_body = md_content
    # Escape HTML tags in content safely
    html_body = html_body.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # Headers
    html_body = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_body, flags=re.MULTILINE)
    
    # Bold / Italic
    html_body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_body)
    html_body = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html_body)
    
    # Checkboxes / Task lists
    html_body = re.sub(r'^- \[ \] (.+)$', r'<li class="task-item"><input type="checkbox" disabled> \1</li>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'^- \[x\] (.+)$', r'<li class="task-item"><input type="checkbox" checked disabled> \1</li>', html_body, flags=re.MULTILINE)
    
    # Bullets
    html_body = re.sub(r'^- (.+)$', r'<li>\1</li>', html_body, flags=re.MULTILINE)
    
    # Horizontal rules
    html_body = re.sub(r'^---$', r'<hr>', html_body, flags=re.MULTILINE)
    
    # Paragraphs (lines separated by double newlines)
    paragraphs = html_body.split('\n\n')
    formatted_p = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if p.startswith('<h') or p.startswith('<li') or p.startswith('<hr'):
            formatted_p.append(p)
        else:
            p_clean = p.replace('\n', '<br>')
            formatted_p.append(f'<p>{p_clean}</p>')
            
    content_html = '\n'.join(formatted_p)

    template = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #0F172A;
            --card-bg: #1E293B;
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --accent: #38BDF8;
            --accent-gold: #F59E0B;
            --border: #334155;
            --success: #10B981;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: 'Heebo', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            direction: rtl;
            text-align: right;
            line-height: 1.8;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 860px;
            margin: 0 auto;
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }}
        .header-badge {{
            display: inline-block;
            background: rgba(56, 189, 248, 0.15);
            color: var(--accent);
            padding: 6px 16px;
            border-radius: 999px;
            font-size: 0.9rem;
            font-weight: 700;
            margin-bottom: 20px;
            border: 1px solid rgba(56, 189, 248, 0.3);
        }}
        h1 {{
            font-size: 2.2rem;
            font-weight: 900;
            color: #FFFFFF;
            margin-bottom: 24px;
            line-height: 1.3;
            border-bottom: 2px solid var(--border);
            padding-bottom: 16px;
        }}
        h2 {{
            font-size: 1.45rem;
            font-weight: 800;
            color: var(--accent-gold);
            margin-top: 36px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        h3 {{
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--accent);
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        p {{
            margin-bottom: 16px;
            color: #E2E8F0;
            font-size: 1.05rem;
        }}
        ul, ol {{
            margin-right: 24px;
            margin-bottom: 20px;
        }}
        li {{
            margin-bottom: 10px;
            font-size: 1.05rem;
            color: #E2E8F0;
        }}
        .task-item {{
            list-style: none;
            display: flex;
            align-items: center;
            gap: 12px;
            background: rgba(15, 23, 42, 0.6);
            padding: 12px 16px;
            border-radius: 10px;
            border: 1px solid var(--border);
            margin-bottom: 8px;
        }}
        .task-item input[type="checkbox"] {{
            width: 18px;
            height: 18px;
            accent-color: var(--success);
        }}
        hr {{
            border: 0;
            height: 1px;
            background: var(--border);
            margin: 30px 0;
        }}
        .meta-box {{
            background: rgba(15, 23, 42, 0.4);
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 28px;
            border: 1px solid var(--border);
            font-size: 0.95rem;
            color: var(--text-muted);
        }}
        .meta-box strong {{
            color: var(--text-main);
        }}
        .actions {{
            display: flex;
            gap: 12px;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
        }}
        .btn {{
            background: var(--accent);
            color: #0F172A;
            border: none;
            padding: 10px 22px;
            border-radius: 10px;
            font-weight: 700;
            cursor: pointer;
            text-decoration: none;
            font-family: inherit;
            transition: all 0.2s;
        }}
        .btn:hover {{
            background: #7dd3fc;
            transform: translateY(-2px);
        }}
        @media print {{
            body {{
                background: white;
                color: black;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
                border: none;
                padding: 0;
                color: black;
                background: white;
            }}
            h1, h2, h3, p, li {{
                color: black !important;
            }}
            .actions {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header-badge">✦ סיכום פגישה חכם מבוסס AI</div>
        <div class="meta-box">
            <div>קובץ מקור: <strong>{source_filename}</strong></div>
            <div>הופק בתאריך: <strong>{datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}</strong></div>
        </div>
        {content_html}
        <div class="actions">
            <button class="btn" onclick="window.print()">הדפס / שמור כ-PDF</button>
        </div>
    </div>
</body>
</html>
"""
    return template

class SummaryResult(str):
    category: str
    meeting_title: str
    date_str: str
    md_path: str
    html_path: str
    summary_text: str

def extract_recording_date(file_name, file_path=None):
    """
    Extracts date and time from filename or file metadata.
    Supports WhatsApp format: 'WhatsApp Audio 2026-08-31 at 09.46.56'
    Supports: '250826', '24.08.2026', '3.8.26', '2026-09-03', etc.
    """
    import re
    # 1. WhatsApp format: 'WhatsApp Audio YYYY-MM-DD at HH.MM.SS'
    m_wa = re.search(r'WhatsApp Audio (\d{4})-(\d{2})-(\d{2}) at (\d{2})\.(\d{2})', file_name, re.IGNORECASE)
    if m_wa:
        yyyy, mm, dd, hh, mins = m_wa.groups()
        return f"{int(dd):02d}/{int(mm):02d}/{yyyy} {hh}:{mins}"
        
    m_ptt = re.search(r'PTT-(\d{4})(\d{2})(\d{2})-WA', file_name, re.IGNORECASE)
    if m_ptt:
        yyyy, mm, dd = m_ptt.groups()
        return f"{int(dd):02d}/{int(mm):02d}/{yyyy}"

    # 2. Date with dots or dashes: YYYY-MM-DD or YYYY.MM.DD
    m_ymd = re.search(r'(\d{4})[-_\.](\d{1,2})[-_\.](\d{1,2})', file_name)
    if m_ymd:
        yyyy, mm, dd = m_ymd.groups()
        return f"{int(dd):02d}/{int(mm):02d}/{yyyy}"

    # 3. Date with dots or dashes: DD.MM.YYYY or DD-MM-YYYY
    m_dmy = re.search(r'(\d{1,2})[-_\.](\d{1,2})[-_\.](\d{4})', file_name)
    if m_dmy:
        dd, mm, yyyy = m_dmy.groups()
        return f"{int(dd):02d}/{int(mm):02d}/{yyyy}"
        
    # 4. 2-digit year: DD.MM.YY (e.g. 24.08.26, 3.8.26)
    m_dmy2 = re.search(r'(\d{1,2})[-_\.](\d{1,2})[-_\.](\d{2})\b', file_name)
    if m_dmy2:
        dd, mm, yy = m_dmy2.groups()
        yyyy = f"20{yy}"
        return f"{int(dd):02d}/{int(mm):02d}/{yyyy}"

    # 5. Compact 6 digits YYMMDD or DDMMYY (e.g. 250826 -> 25/08/2026)
    m_compact = re.search(r'\b(\d{2})(\d{2})(\d{2})\b', file_name)
    if m_compact:
        p1, p2, p3 = m_compact.groups()
        if int(p1) <= 31 and 1 <= int(p2) <= 12:
            return f"{p1}/{p2}/20{p3}"
        elif int(p3) <= 31 and 1 <= int(p2) <= 12:
            return f"{p3}/{p2}/20{p1}"

    # 6. Fallback to file creation / modified time
    if file_path and os.path.exists(file_path):
        mtime = os.path.getmtime(file_path)
        return datetime.datetime.fromtimestamp(mtime).strftime('%d/%m/%Y')

    return datetime.datetime.now().strftime('%d/%m/%Y')

def extract_category(summary_text):
    """Detects whether meeting category is 'עסקים' or 'גפ\"ן'."""
    text_lower = summary_text.lower()
    for line in summary_text.splitlines():
        if "**קטגוריה:**" in line:
            if "עסק" in line:
                return "עסקים"
            elif "גפ" in line or "חינוך" in line:
                return "גפ\"ן"
                
    # Heuristic scoring fallback
    business_keywords = ['עסק', 'שחף', 'חשבונית', 'invoice', 'סוכן', 'פיתוח', 'לקוח', 'חברה', 'hubayta', 'שיווק']
    gefen_keywords = ['גפ"ן', 'גפן', 'בית ספר', 'מורה', 'מורות', 'חינוך', 'תל"א', 'תח"י', 'גוונים', 'רננים', 'אלומות', 'אורי', 'הכט', 'פיקוח']
    
    business_score = sum(text_lower.count(k) for k in business_keywords)
    gefen_score = sum(text_lower.count(k) for k in gefen_keywords)
    
    return "עסקים" if business_score > gefen_score else "גפ\"ן"

def extract_meeting_title(summary_text, default_name="פגישה"):
    """Extracts meeting title from summary text."""
    import re
    m = re.search(r'^# סיכום פגישה:\s*(.+)$', summary_text, re.MULTILINE)
    if m:
        title = m.group(1).strip()
        title = re.sub(r'[\[\]]', '', title).strip()
        if title:
            return title
    return os.path.splitext(default_name)[0]

def extract_meeting_date_from_summary(summary_text):
    """Extracts date string from generated summary."""
    import re
    m = re.search(r'\*\*תאריך.*?\:\*\*\s*(.+)$', summary_text, re.MULTILINE)
    if m:
        d = m.group(1).strip()
        d = re.sub(r'[\[\]]', '', d).strip()
        if d:
            return d
    return None

def append_to_master_summary(summary_text, category, meeting_title, date_str):
    """
    Appends the meeting summary to the relevant local master file:
    - Business -> MASTER_BUSINESS_SUMMARY_FILE
    - Gefen -> MASTER_GEFEN_SUMMARY_FILE
    """
    target_file = config.MASTER_BUSINESS_SUMMARY_FILE if category == 'עסקים' else config.MASTER_GEFEN_SUMMARY_FILE
    
    if not os.path.exists(os.path.dirname(target_file)):
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        
    # Read existing content if file exists
    if os.path.exists(target_file):
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        title_header = "# 💼 ריכוז סיכומי פגישות עסקיות - הדיאלוג הדיגיטלי" if category == 'עסקים' else "# 📋 ריכוז סיכומי פגישות עבודה - הדיאלוג הדיגיטלי"
        desc = "קובץ זה מאגד את כלל סיכומי פגישות העבודה, הפרוטוקולים והאוטומציות שנבנו עבור לקוחות עסקיים (בנפרד מתוכניות החינוך והגפ\"ן)." if category == 'עסקים' else "קובץ זה מאגד את כלל סיכומי פגישות העבודה והפרוטוקולים שהתקיימו במסגרת הפרויקטים השונים של \"הדיאלוג הדיגיטלי\"."
        content = f"{title_header}\n\n{desc}\n\n---\n\n## 🔗 ניווט מהיר\n\n---\n"

    # Avoid duplicate entry if this title and date already exists
    search_key = f"{meeting_title} - {date_str}"
    if search_key in content or meeting_title in content:
        print(f"ℹ️ הפגישה '{meeting_title}' כבר קיימת בקובץ הריכוז: {os.path.basename(target_file)}")
        return target_file

    # Find next index from navigation list
    import re
    nav_pattern = r'## 🔗 ניווט מהיר\s*\n((?:(?:\d+\.|\*)\s*\[.+?\]\(.+?\)\s*\n*)*)'
    match = re.search(nav_pattern, content)
    
    current_items = []
    if match:
        nav_block = match.group(1)
        current_items = re.findall(r'(\d+)\.\s*\[(.+?)\]\((.+?)\)', nav_block)
        
    next_idx = len(current_items) + 1
    
    # Create anchor slug
    clean_anchor = re.sub(r'[^a-zA-Z0-9\u0590-\u05FF]+', '-', f"{next_idx}-{meeting_title}-{date_str}").strip('-').lower()
    nav_entry = f"{next_idx}. [{meeting_title} ({date_str})](#{clean_anchor})"
    
    # Format entry content:
    lines = summary_text.strip().splitlines()
    body_lines = []
    skip_header = True
    for line in lines:
        if skip_header and (line.startswith("# ") or line.startswith("**נושא")):
            continue
        if skip_header and line.strip() == "---":
            skip_header = False
            continue
        if not skip_header:
            # Demote ## headings to ###
            if line.startswith("## "):
                body_lines.append("#" + line)
            else:
                body_lines.append(line)
                
    formatted_body = "\n".join(body_lines).strip()
    entry_text = f"\n\n---\n\n## {next_idx}. {meeting_title} - {date_str}\n\n{formatted_body}\n"
    
    # Insert new item into navigation section
    if match:
        if nav_block.strip():
            new_nav_block = nav_block.rstrip() + f"\n{nav_entry}\n"
        else:
            new_nav_block = f"{nav_entry}\n"
        content = content[:match.start(1)] + new_nav_block + content[match.end(1):]
    else:
        content = content + f"\n## 🔗 ניווט מהיר\n{nav_entry}\n\n---\n"
        
    # Append entry to end of file
    content = content.rstrip() + entry_text
    
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"   ✓ קובץ הריכוז עודכן בהצלחה: {os.path.basename(target_file)} (נוספה פגישה #{next_idx})")
    return target_file

def summarize_audio_file(audio_path, display_name=None):
    import warnings
    warnings.filterwarnings("ignore")
    
    if not os.path.exists(audio_path):
        print(f"שגיאה: הקובץ לא נמצא: {audio_path}")
        return None
        
    file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
    file_name = display_name or os.path.basename(audio_path)
    mime_type = get_mime_type(file_name)
    extracted_date = extract_recording_date(file_name, audio_path)
    
    print("=" * 60)
    print(f"מתחיל תהליך סיכום פגישה:")
    print(f"קובץ: {file_name}")
    print(f"תאריך שחולץ: {extracted_date}")
    print(f"גודל קובץ: {file_size_mb:.2f} MB")
    print(f"סוג מדיה: {mime_type}")
    print("=" * 60)
    
    os.makedirs(SUMMARIES_DIR, exist_ok=True)
    
    # Initialize Gemini client
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    
    uploaded_file = None
    if file_size_mb < 20:
        print("\n1. קורא את קובץ השמע לעיבוד ישיר ומהיר ב-Gemini...")
        with open(audio_path, "rb") as f:
            audio_data = f.read()
        audio_content = types.Part.from_bytes(data=audio_data, mime_type=mime_type)
        print("   ✓ הקובץ נטען ומועבר ישירות למודל (ללא צורך בהמתנה להמרה בענן)")
    else:
        print("\n1. מעלה את קובץ השמע לעיבוד ב-Gemini (קובץ גדול)...")
        start_upload = time.time()
        
        # Ensure ASCII path for httpx upload header compatibility
        ext = os.path.splitext(audio_path)[1]
        upload_path = audio_path
        cleanup_temp = False
        if not audio_path.isascii():
            import shutil
            import tempfile
            safe_temp = os.path.join(tempfile.gettempdir(), f"audio_up_{int(time.time())}_{os.getpid()}{ext}")
            shutil.copy2(audio_path, safe_temp)
            upload_path = safe_temp
            cleanup_temp = True
            
        try:
            uploaded_file = client.files.upload(
                file=upload_path,
                config=types.UploadFileConfig(mime_type=mime_type, display_name="meeting_audio") if mime_type else None
            )
        finally:
            if cleanup_temp and os.path.exists(upload_path):
                try:
                    os.remove(upload_path)
                except Exception:
                    pass
                    
        print(f"   ✓ הקובץ הועלה בהצלחה (משך העלאה: {time.time() - start_upload:.1f} שניות)")
        
        while uploaded_file.state.name == "PROCESSING":
            print("   ממתין לסיום עיבוד הקובץ בשרתי Google...")
            time.sleep(3)
            uploaded_file = client.files.get(name=uploaded_file.name)
            
        if uploaded_file.state.name == "FAILED":
            raise Exception(f"עיבוד הקובץ נכשל: {uploaded_file.error.message}")
            
        audio_content = uploaded_file
        
    print("\n2. מתמלל ומנתח את הפגישה ומפיק סיכום מובנה בעברית...")
    start_gen = time.time()
    
    dynamic_prompt = PROMPT_MEETING_SUMMARY + f"\n\nהקשר נוסף שנמצא:\n- שם הקובץ: {file_name}\n- תאריך ושעה שחולצו מקובץ ההקלטה: {extracted_date} (השתמש בתאריך זה בשדה התאריך אלא אם צוין תאריך אחר מפורשות בשיחה)."
    
    response = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=[
            audio_content,
            dynamic_prompt
        ]
    )
    
    summary_text = response.text
    print(f"   ✓ הסיכום הופק בהצלחה! (משך עיבוד AI: {time.time() - start_gen:.1f} שניות)")
    
    # Delete uploaded file from Gemini cloud storage if one was created
    if uploaded_file:
        try:
            client.files.delete(name=uploaded_file.name)
        except Exception:
            pass
        
    # Analyze metadata
    category = extract_category(summary_text)
    meeting_title = extract_meeting_title(summary_text, file_name)
    meeting_date = extract_meeting_date_from_summary(summary_text) or extracted_date
    
    print(f"\n📊 סיווג פגישה: '{category}' | כותרת: '{meeting_title}' | תאריך: '{meeting_date}'")
    
    # Save outputs locally
    now_str = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    base_output_name = f"סיכום_פגישה_{now_str}_{os.path.splitext(file_name)[0]}"
    
    md_file_path = os.path.join(SUMMARIES_DIR, f"{base_output_name}.md")
    html_file_path = os.path.join(SUMMARIES_DIR, f"{base_output_name}.html")
    
    with open(md_file_path, "w", encoding="utf-8") as f:
        f.write(summary_text)
        
    html_content = generate_html_summary(summary_text, f"סיכום פגישה - {file_name}", file_name)
    with open(html_file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print("\n" + "=" * 60)
    print(f"הסיכום נשמר בהצלחה בתיקיית הסיכומים:")
    print(f"• קובץ Markdown: {md_file_path}")
    print(f"• קובץ HTML מעוצב: {html_file_path}")
    print("=" * 60)
    
    # Update local master summary file
    try:
        append_to_master_summary(summary_text, category, meeting_title, meeting_date)
    except Exception as e:
        print(f"⚠️ שגיאה בעדכון קובץ הריכוז המרכזי: {e}")
    
    # Open HTML summary in default browser
    try:
        webbrowser.open(f"file:///{os.path.abspath(html_file_path)}")
    except Exception as e:
        print(f"לא ניתן היה לפתוח את הדפדפן אוטומטית: {e}")
        
    # Build enriched return object compatible with string
    res = SummaryResult(html_file_path)
    res.category = category
    res.meeting_title = meeting_title
    res.date_str = meeting_date
    res.md_path = md_file_path
    res.html_path = html_file_path
    res.summary_text = summary_text
    return res

def select_file_dialog():
    import tkinter as tk
    from tkinter import filedialog
    
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    file_path = filedialog.askopenfilename(
        title="בחר קובץ הקלטה לסיכום פגישה",
        filetypes=[
            ("קובצי שמע ווידאו", "*.m4a;*.mp3;*.wav;*.aac;*.ogg;*.flac;*.mp4;*.webm;*.mov"),
            ("קובצי שמע (m4a, mp3, wav)", "*.m4a;*.mp3;*.wav;*.aac;*.ogg"),
            ("כל הקבצים", "*.*")
        ]
    )
    root.destroy()
    return file_path

if __name__ == "__main__":
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
    else:
        print("לא סופק קובץ בפקודה. פותח חלון לבחירת קובץ הקלטה...")
        audio_file = select_file_dialog()
        
    if not audio_file:
        print("לא נבחר קובץ. היציאה מהתוכנית.")
        sys.exit(0)
        
    try:
        summarize_audio_file(audio_file)
    except Exception as e:
        print(f"\n❌ שגיאה במהלך הסיכום: {e}")
        import traceback
        traceback.print_exc()
        if sys.stdin and sys.stdin.isatty():
            try:
                input("\nלחץ Enter לסגירה...")
            except (EOFError, KeyboardInterrupt):
                pass
        sys.exit(1)
