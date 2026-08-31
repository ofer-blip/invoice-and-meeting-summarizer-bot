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
אתה עוזר מקצועי לניהול, תמלול וסיכום פגישות עסקיות ואסטרטגיות בעברית.
האזן היטב לקובץ השמע המצורף של הפגישה/השיחה, והפק סיכום מקיף, תכליתי ומסודר היטב בעברית טבעית ורהוטה.

חשוב מאוד: הקפד על חלוקה מרווחת וקריאה, שבה כל נושא, החלטה ותובנה מופיעים בשורה נפרדת (ולא כגוש טקסט רציף).

אנא בנה את הסיכום לפי המבנה המדויק הבא:

# סיכום פגישה: [נושא הפגישה המרכזי]

**תאריך ושעה משוערת:** [אם מוזכר בשיחה, אחרת רשום תאריך נוכחי]
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
*הערה: שמור על עברית טבעית, מקצועית וברורה, תוך שמירה על הקשר עסקי מדויק וריווח מלא בין פסקאות.*
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

def summarize_audio_file(audio_path, display_name=None):
    import warnings
    warnings.filterwarnings("ignore")
    
    if not os.path.exists(audio_path):
        print(f"שגיאה: הקובץ לא נמצא: {audio_path}")
        return None
        
    file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
    file_name = display_name or os.path.basename(audio_path)
    mime_type = get_mime_type(file_name)
    
    print("=" * 60)
    print(f"מתחיל תהליך סיכום פגישה:")
    print(f"קובץ: {file_name}")
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
    
    response = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=[
            audio_content,
            PROMPT_MEETING_SUMMARY
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
        
    # Save outputs
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
    
    # Open HTML summary in default browser
    try:
        webbrowser.open(f"file:///{os.path.abspath(html_file_path)}")
    except Exception as e:
        print(f"לא ניתן היה לפתוח את הדפדפן אוטומטית: {e}")
        
    return html_file_path

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
