import config
from google import genai
from google.genai import types

STORY_PROMPT = """
אתה מספר סיפורים יצירתי ומרתק.
קרא את תמלול הפגישה או סיכום הפגישה המצורף, שלוף ממנו משפט מפתח אחד משמעותי, וכתוב סיפור קצר ומרתק (עד 3 פסקאות) בהשראתו.
הסיפור יכול להתרחש בכל זמן ובכל מקום בעולם, עליו להיות ספרותי ומרתק, ומטרתו להעביר תובנה או לקח חשוב מתוך הפגישה (מבלי לציין שזה מתוך פגישה מפורשות).
התחל את הסיפור עם משפט המפתח שבחרת.
"""

def generate_story(text_input):
    if not text_input:
        return "אין טקסט זמין ליצירת סיפור."
        
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    response = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=[
            types.Part.from_text(text=f"{STORY_PROMPT}\n\nטקסט להשראה:\n{text_input}")
        ]
    )
    return response.text
