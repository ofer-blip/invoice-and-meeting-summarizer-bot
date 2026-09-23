import os
import requests
import time
import json
import config

def transcribe_and_diarize(audio_path):
    api_key = config.DEEPGRAM_API_KEY
    if not api_key:
        print("⚠️ שגיאה: לא הוגדר מפתח Deepgram ב-config.py")
        return None, None
        
    url = "https://api.deepgram.com/v1/listen?model=general&tier=nova-3&language=he&diarize=true&smart_format=true"
    headers = {
        "Authorization": f"Token {api_key}"
    }
    
    print(f"\n   [Deepgram] מעלה קובץ שמע לתמלול עמוק ({os.path.basename(audio_path)})...")
    start_time = time.time()
    
    try:
        with open(audio_path, 'rb') as audio_file:
            response = requests.post(url, headers=headers, data=audio_file, timeout=1200)
            
        if response.status_code != 200:
            print(f"   [Deepgram] ❌ שגיאה מהשרת ({response.status_code}): {response.text}")
            return None, None
            
        data = response.json()
        print(f"   [Deepgram] ✓ התמלול הסתיים בהצלחה (משך זמן: {time.time() - start_time:.1f} שניות)")
        
        transcript_md = _format_diarization(data)
        return transcript_md, data
        
    except Exception as e:
        print(f"   [Deepgram] ❌ שגיאה חמורה: {str(e)}")
        return None, None

def _format_diarization(data):
    try:
        words = data['results']['channels'][0]['alternatives'][0]['words']
    except KeyError:
        return "שגיאה בפיענוח מבנה הנתונים של Deepgram."
        
    if not words:
        return "לא זוהה דיבור בהקלטה זו."

    lines = []
    current_speaker = words[0].get('speaker', 0)
    current_sentence = []
    
    for word_info in words:
        word = word_info['punctuated_word']
        speaker = word_info.get('speaker', 0)
        
        if speaker != current_speaker:
            lines.append(f"**דובר {current_speaker}:** {' '.join(current_sentence)}")
            current_speaker = speaker
            current_sentence = [word]
        else:
            current_sentence.append(word)
            
    if current_sentence:
        lines.append(f"**דובר {current_speaker}:** {' '.join(current_sentence)}")
        
    return "\n\n".join(lines)

def get_html_transcript(transcript_md, title):
    import re
    html_body = transcript_md.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    html_body = re.sub(r'\*\*(.+?):\*\*', r'<strong>\1:</strong>', html_body)
    paragraphs = [f"<p>{p.strip()}</p>" for p in html_body.split('\n\n') if p.strip()]
    template = f'''<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;700;800&display=swap" rel="stylesheet">
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
        h1 {{
            color: #111827;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 10px;
        }}
        p {{ margin-bottom: 15px; font-size: 14px; }}
        strong {{ color: #1f2937; font-weight: bold; margin-left: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        {''.join(paragraphs)}
    </div>
</body>
</html>'''
    return template
