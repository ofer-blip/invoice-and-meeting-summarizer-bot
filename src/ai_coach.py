import config
from google import genai
from google.genai import types

COACH_PROMPT = """
אתה מאמן אישי עסקי ופדגוגי בסגנון של 'אלון אולמן' (הקוד המנצח, פריצת גבולות). להלן תמלול של פגישה שקיימתי.
מטרתך היא לנתח את הביצועים שלי בפגישה ולהפיק דוח מאמן בסגנון האנרגטי, הבלתי מתפשר והמעצים של אלון אולמן. 
השתמש במונחים כמו "פריצת גבולות", "השאלה היא לא אם אני יכול, אלא מה אני מוכן לעשות", ו"הצלחה היא מדע מדויק".

המבנה הנדרש (הקפד להשתמש בשורות ריקות לפני רשימות!):

## 🚀 ניתוח המאמן האישי (בסגנון הקוד המנצח)

**רמת אנרגיה ותשוקה בפגישה:** 
[פסקה קצרה ותוססת על הגישה שניכרה בשיחה]

### 🔥 3 נקודות לשימור (מה עשית כמו מנצח):

* [נקודה 1]
* [נקודה 2]
* [נקודה 3]

### 🚧 3 תקרות זכוכית לנפץ (מה דורש פריצת גבולות):

* [נקודה 1]
* [נקודה 2]
* [נקודה 3]

**משפט מחץ לסיום:** 
[משפט השראה חזק בסגנון של אלון אולמן]
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
