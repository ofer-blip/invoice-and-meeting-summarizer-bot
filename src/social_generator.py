import config
from google import genai
from google.genai import types

SOCIAL_PROMPT = """
אתה מומחה סושיאל. קרא את הפגישה המצורפת והפק:
1. פוסט פייסבוק קצר וקולע (בעברית) שמשתף תובנה מרכזית אחת בלי לחשוף סודות עסקיים.
2. משפט באנגלית (פרומפט) ליצירת תמונה (Image generation prompt) מלווה. הפרומפט חייב לכלול את ההנחיה המפורשת ליצור תמונה בסגנון: 'initial sketch by Susan Waldon'.

החזר את התשובה בפורמט מובנה בדיוק כך:
--- פוסט ---
[הפוסט שלך כאן]
--- פרומפט תמונה ---
[הפרומפט כאן]
"""

def generate_social_content(text_input):
    if not text_input:
        return "אין טקסט", ""
        
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    response = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=[
            types.Part.from_text(text=f"{SOCIAL_PROMPT}\n\nטקסט הפגישה:\n{text_input}")
        ]
    )
    
    text = response.text
    post = ""
    img_prompt = ""
    
    try:
        parts = text.split("--- פרומפט תמונה ---")
        img_prompt = parts[1].strip()
        post = parts[0].replace("--- פוסט ---", "").strip()
    except Exception:
        post = text
        img_prompt = "A minimal black and white initial sketch by Susan Waldon representing business insights"
        
    return post, img_prompt

def generate_image(prompt):
    try:
        client = genai.Client(api_key=config.GEMINI_API_KEY)
        result = client.models.generate_images(
            model='imagen-3.0-generate-001',
            prompt=prompt,
            config=dict(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="1:1"
            )
        )
        for generated_image in result.generated_images:
            return generated_image.image.image_bytes
    except Exception as e:
        print(f"⚠️ שגיאה ביצירת תמונה עם Imagen: {e}")
        return None
