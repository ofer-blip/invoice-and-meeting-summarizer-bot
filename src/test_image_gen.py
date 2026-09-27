import os
import config
import image_generator

# Make sure to put your OpenAI API key in config.py first!
print("OpenAI API Key:", config.OPENAI_API_KEY)

summary_text = """
# סיכום פגישה: תכנון פרויקט דירת האימון
* תאריך: 25.08.2026
* נכחו: עופר, שחף, צוות הפיתוח
* נושא מרכזי: פגישת התנעה והגדרת יעדים לדירת האימון של החניכים.

## נושא השיחה המרכזי
הפגישה עסקה בבניית תוכנית עבודה לשילוב החניכים בסביבת דירת האימון.
שמנו דגש על עצמאות, שיתוף פעולה ובניית חזון משותף.
"""

print("\n--- מתחיל בדיקה של מחולל התמונות ---")
url = image_generator.generate_meeting_illustration(summary_text)

if url:
    print("\n✅ הצלחה! התמונה נוצרה. הנה הקישור:")
    print(url)
else:
    print("\n❌ נכשל. ודא שהכנסת מפתח API ושספרית openai מותקנת.")
