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
1. הקפד על חלוקה מרווחת וקריאה. בכל נקודה חדשה (מצוינת בכוכבית), חובה להתחיל שורה חדשה לחלוטין.
2. קצר ותמצת את נקודות המפתח. אל תאריך במילים היכן שאין צורך.
3. סווג את הפגישה במדויק בשדה הקטגוריה. בחר אך ורק מתוך הקטגוריות הבאות: {CATEGORIES_LIST}.
"""

DEFAULT_STRUCTURE = """
אנא בנה את הסיכום לפי המבנה המדויק הבא:

# סיכום פגישה: [נושא הפגישה המרכזי]

**תאריך ושעה:** [תאריך ושעת הפגישה]
**קטגוריה:** [{CATEGORIES_PLACEHOLDER}]
**משתתפים/דוברים שזוהו:** [שמות הדוברים או תפקידים שזוהו במהלך השיחה]
**נושא מרכזי:** [משפט אחד שמסביר את מהות הפגישה]

---

## 1. תקציר מנהלים (Executive Summary)
[2-3 פסקאות קצרות וממוקדות שמסבירות את הרקע, הצורך והכיוונים המרכזיים].

## 2. נקודות מפתח ונושאים שנדונו
(קצר ותמצת! הקפד להתחיל שורה חדשה לכל נקודה עם כוכבית):

* **[נושא 1]:** [משפט תמציתי קצרצר על מה שנדון]
* **[נושא 2]:** [משפט תמציתי קצרצר על מה שנדון]
* **[נושא 3]:** [משפט תמציתי קצרצר על מה שנדון]

## 3. החלטות שהתקבלו
(רשימה ממוספרת שבה כל החלטה מופיעה בשורה נפרדת לחלוטין):
1. **[החלטה ראשונה]:** [פירוט קצר של מה שהוחלט]
2. **[החלטה שנייה]:** [פירוט קצר של מה שהוחלט]

## 4. משימות לביצוע ותוכנית פעולה (Action Items)
(הצג בטבלה פשוטה):

| משימה | באחריות | יעד / הערות |
| :--- | :---: | :---: |
| [תיאור משימה קצר] | [שם האחראי] | [יעד או הערה] |
| [תיאור משימה קצר] | [שם האחראי] | [יעד או הערה] |

## 5. תובנות ודגשים להמשך
(הקפד שכל תובנה תהיה בנקודה נפרדת בשורה משלה):

* **[תובנה 1]:** [דגש, הזדמנות או נושא למעקב]
* **[תובנה 2]:** [דגש, הזדמנות או נושא למעקב]

---
*הערה: שמור על עברית טבעית, מקצועית וברורה, תוך הקפדה חמורה על ירידת שורה בכל פעם שמתחילים נקודה חדשה.*
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
    import markdown
    
    # Render markdown to HTML with tables extension
    html_body = markdown.markdown(md_content, extensions=['tables'])
    html_body = html_body.replace('<table>', '<table border="1" cellpadding="8" style="border-collapse: collapse; width: 100%; border: 1px solid #d1d5db;">')
    
    # Wrap in clean, print-friendly, email-friendly HTML
    template = f'''<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #ffffff;
            color: #000000;
            direction: rtl;
            text-align: right;
            line-height: 1.6;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        h1, h2, h3 {{ color: #111827; margin-top: 20px; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }}
        th, td {{
            border: 1px solid #d1d5db;
            padding: 12px;
            text-align: right;
        }}
        th {{
            background-color: #f3f4f6;
            font-weight: bold;
            color: #374151;
        }}
        tr:nth-child(even) {{ background-color: #f9fafb; }}
        hr {{ border: 0; border-top: 1px solid #e5e7eb; margin: 20px 0; }}
        a {{ color: #2563eb; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        {html_body}
    </div>
</body>
</html>'''
    return template

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


def extract_recording_date(file_name, audio_path):
    import datetime
    import re
    # Try to extract date from filename, else return current date
    match = re.search(r'\d{4}-\d{2}-\d{2}', file_name)
    if match:
        return match.group(0)
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

def summarize_audio_file(audio_path, display_name=None, categories=None, manual_category=None):
    import warnings
    warnings.filterwarnings("ignore")
    
    if categories is None:
        categories = [{"name": "כללי", "prompt": ""}]
        
    # Support both list of strings (legacy) and list of dicts (new)
    cat_names = []
    cat_dict = {}
    for c in categories:
        if isinstance(c, str):
            cat_names.append(c)
            cat_dict[c] = ""
        else:
            cat_names.append(c.get("name", ""))
            cat_dict[c.get("name", "")] = c.get("prompt", "")
            
    categories_list = ", ".join([f"'{c}'" for c in cat_names if c])
    categories_placeholder = " / ".join([c for c in cat_names if c])
    
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
    if manual_category:
        print(f"סיווג ידני: {manual_category} (מדלג על סיווג אוטומטי)")
    print("=" * 60)
    
    os.makedirs(SUMMARIES_DIR, exist_ok=True)
    
    # Check if transcription is requested
    should_transcribe = False
    if manual_category:
        for c in categories:
            if isinstance(c, dict) and c.get("name") == manual_category:
                should_transcribe = c.get("transcribe", False)
                break
    else:
        # Default to the first category (General) if dropped in root
        if categories and isinstance(categories[0], dict):
            should_transcribe = categories[0].get("transcribe", False)
            
    transcript_md = None
    transcript_data = None
    
    if should_transcribe:
        import transcriber
        transcript_md, transcript_data = transcriber.transcribe_and_diarize(audio_path)
    else:
        print("\n1. תמלול מלא כבוי עבור תיקייה זו (מדלג על Deepgram)...")
        
    # Initialize Gemini client
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    
    uploaded_file = None
    if transcript_md:
        print("\n1. משתמש בטקסט שתומלל מ-Deepgram כקלט ל-Gemini...")
        audio_content = types.Part.from_text(text=f"להלן תמלול מלא של הפגישה:\n\n{transcript_md}")
    else:
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
    
    # Format the prompt
    base_prompt = PROMPT_MEETING_SUMMARY.replace("{CATEGORIES_LIST}", categories_list)
    
    dynamic_prompt = base_prompt + f"\n\nהקשר נוסף שנמצא:\n- שם הקובץ: {file_name}\n- תאריך ושעה שחולצו מקובץ ההקלטה: {extracted_date} (השתמש בתאריך זה בשדה התאריך אלא אם צוין תאריך אחר מפורשות בשיחה)."
    
    # Apply custom prompt if available
    target_cat = manual_category if manual_category else None
    if target_cat:
        if target_cat in cat_dict and cat_dict[target_cat]:
            custom_instructions = cat_dict[target_cat]
            print(f"   ✓ מפעיל תבנית סיכום מותאמת אישית עבור התיקייה: {target_cat}")
            dynamic_prompt += f"\n\nהנחיות עיצוב ומבנה מיוחדות למשתמש זה (חובה לציית! התעלם מכל מבנה אחר):\n{custom_instructions}"
        else:
            print(f"   ✓ מפעיל תבנית ברירת מחדל עבור התיקייה: {target_cat}")
            dynamic_prompt += f"\n\n{DEFAULT_STRUCTURE.replace('{CATEGORIES_PLACEHOLDER}', target_cat)}"
    else:
        # Auto category: provide default structure but override per category if needed
        has_custom = False
        custom_prompts_text = "\n\nהנחיות עיצוב ומבנה מיוחדות (חובה לציית להנחיה של הקטגוריה שבחרת - היא דורסת את מבנה ברירת המחדל!):\n"
        for cname, cprompt in cat_dict.items():
            if cprompt:
                has_custom = True
                custom_prompts_text += f"אם בחרת לסווג כ-'{cname}', עליך לעצב את הסיכום בדיוק לפי המבנה וההנחיות הבאות: {cprompt}\n"
        
        dynamic_prompt += f"\n\n{DEFAULT_STRUCTURE.replace('{CATEGORIES_PLACEHOLDER}', categories_placeholder)}"
        if has_custom:
            dynamic_prompt += custom_prompts_text
            
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
    category = manual_category if manual_category else extract_category(summary_text)
    
    # If AI hallucinated a category, fallback to the first one
    if category not in cat_names and not manual_category:
        category = cat_names[0] if cat_names else "כללי"
        
    meeting_title = extract_meeting_title(summary_text, file_name)
    meeting_date = extract_meeting_date_from_summary(summary_text) or extracted_date
    
    print(f"\n📊 סיווג פגישה: '{category}' | כותרת: '{meeting_title}' | תאריך: '{meeting_date}'")
    
    # Save outputs locally
    now_str = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    base_output_name = f"סיכום_פגישה_{now_str}_{os.path.splitext(file_name)[0]}"
    
    md_file_path = os.path.join(SUMMARIES_DIR, f"{base_output_name}.md")
    html_file_path = os.path.join(SUMMARIES_DIR, f"{base_output_name}.html")
    
    with open(md_file_path, "w", encoding="utf-8") as f:
        f.write('<div dir="rtl">\n\n' + summary_text + '\n\n</div>')

        
    html_content = generate_html_summary(summary_text, f"סיכום פגישה - {file_name}", file_name)
    with open(html_file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    transcript_md_path = None
    transcript_html_path = None
    if transcript_md:
        base_transcript_name = f"תמלול_מלא_{now_str}_{os.path.splitext(file_name)[0]}"
        transcript_md_path = os.path.join(SUMMARIES_DIR, f"{base_transcript_name}.md")
        transcript_html_path = os.path.join(SUMMARIES_DIR, f"{base_transcript_name}.html")
        
        with open(transcript_md_path, "w", encoding="utf-8") as f:
            f.write(transcript_md)
            
        transcript_html = transcriber.get_html_transcript(transcript_md, f"תמלול מלא - {file_name}")
        with open(transcript_html_path, "w", encoding="utf-8") as f:
            f.write(transcript_html)
        print(f"• קובץ תמלול מלא נוצר בהצלחה.")
        
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
    class SummaryResult(str):
        pass
    res = SummaryResult(html_file_path)
    res.category = category
    res.meeting_title = meeting_title
    res.date_str = meeting_date
    res.md_path = md_file_path
    res.html_path = html_file_path
    res.transcript_md_path = transcript_md_path
    res.transcript_html_path = transcript_html_path
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
