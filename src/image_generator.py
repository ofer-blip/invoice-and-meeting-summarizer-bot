import os
import sys
import traceback
from google import genai
try:
    import openai
except ImportError:
    pass

import config

def generate_image_prompt(summary_text, style="minimalist continuous single line drawing"):
    """
    Uses Gemini to read the Hebrew summary and generate a descriptive English prompt 
    for an image generator (like DALL-E) based on the chosen style.
    """
    if not config.GEMINI_API_KEY:
        print("Missing Gemini API Key for image prompt generation.")
        return None
        
    try:
        client = genai.Client(api_key=config.GEMINI_API_KEY)
        
        system_instruction = f"""
You are an expert creative director. 
I will provide you with a meeting summary in Hebrew. 
Your task is to write a single, highly descriptive English prompt for an AI image generator (like DALL-E) that visualizes the essence of the meeting.

Guidelines:
1. The image MUST be in this specific style: {style}.
2. Describe the scene, the subjects, and the atmosphere metaphorically or directly based on the summary.
3. Keep it under 60 words.
4. Output ONLY the English prompt, without any introductions, quotes, or markdown.
"""

        response = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=[
                system_instruction,
                "Meeting summary:\n" + summary_text
            ]
        )
        prompt = response.text.strip()
        return prompt
    except Exception as e:
        print(f"Error generating image prompt: {e}")
        return None

def generate_meeting_illustration(summary_text):
    """
    Full pipeline: Summary -> English Prompt -> Image URL via DALL-E 3.
    """
    openai_key = getattr(config, 'OPENAI_API_KEY', None)
    if not openai_key:
        print("⚠️ OPENAI_API_KEY לא מוגדר בקובץ config.py. מדלג על יצירת איור.")
        return None
        
    try:
        import openai
    except ImportError:
        print("⚠️ ספרית openai לא מותקנת. יש להריץ: pip install openai")
        return None
        
    print("\n🎨 מתחיל תהליך יצירת איור לסיכום...")
    
    # Step 1: Create the prompt using Gemini
    english_prompt = generate_image_prompt(summary_text)
    if not english_prompt:
        return None
        
    print(f"   ✓ פרומפט לתמונה נוצר: {english_prompt}")
    
    # Step 2: Call OpenAI DALL-E 3 API
    try:
        openai_client = openai.OpenAI(api_key=openai_key)
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=english_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        print(f"   ✓ איור נוצר בהצלחה!")
        return image_url
    except Exception as e:
        print(f"⚠️ שגיאה ביצירת תמונה מול OpenAI: {e}")
        traceback.print_exc()
        return None
