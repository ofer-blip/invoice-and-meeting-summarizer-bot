import config
from google import genai
from google.genai import types

COACH_PROMPT = """
אתה מאמן אישי עסקי ופדגוגי (AI Coach). להלן תמלול של פגישה שקיימתי.
מטרתך היא לנתח את הביצועים שלי, את סגנון הדיבור, טון השיחה, ולהציג נקודות לשימור ולשיפור.
כתוב את הדוח בעברית טבעית, בגוף שני, והיה כן, מעצים ומקצועי.

אנא ספק:
1. סקירה כללית של טון השיחה.
2. 2-3 נקודות לשימור.
3. 2-3 נקודות לשיפור.
"""

def generate_coach_report(transcript_text):
    if not transcript_text:
        return "לא סופק תמלול לניתוח."
        
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    response = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=[
            types.Part.from_text(text=f"{COACH_PROMPT}\n\nתמלול השיחה:\n{transcript_text}")
        ]
    )
    return response.text
