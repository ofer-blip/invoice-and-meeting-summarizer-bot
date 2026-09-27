import os

def run_extended_pipeline(drive_svc, target_category_folder_id, actual_md_path, transcript_md_path, summary_text, upload_callback):
    """
    Runs the extended AI pipeline (Coach, Story, Social) and uploads the results to Google Drive.
    """
    try:
        import ai_coach
        import story_engine
        import social_generator
        import os
        
        transcript_text = ""
        if transcript_md_path and os.path.exists(transcript_md_path):
            with open(transcript_md_path, 'r', encoding='utf-8') as tf:
                transcript_text = tf.read()
                
        text_for_ai = transcript_text if transcript_text else summary_text
        
        print("   - מפעיל AI Coach (מאמן אישי)...")
        coach_report = ai_coach.generate_coach_report(text_for_ai)
        
        print("   - מפעיל Story Engine (מספר סיפורים)...")
        story_text = story_engine.generate_story(text_for_ai)
        
        print("   - מפעיל Social Generator (סושיאל)...")
        post_text, img_prompt = social_generator.generate_social_content(text_for_ai)
        
        # Combine all into one beautiful HTML
        import markdown
        
        html_content = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2563eb; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }}
        h2 {{ color: #1e40af; margin-top: 30px; }}
        h3 {{ color: #3b82f6; }}
        .section {{ background: #f8fafc; border-radius: 8px; padding: 20px; margin-bottom: 25px; border: 1px solid #e2e8f0; }}
        .prompt-box {{ background: #1e293b; color: #f8fafc; padding: 15px; border-radius: 5px; font-family: monospace; direction: ltr; text-align: left; }}
    </style>
</head>
<body>
    <h1>🚀 תובנות AI חכמות (D-Dialog)</h1>
    
    <div class="section">
        {markdown.markdown(coach_report)}
    </div>
    
    <div class="section">
        {markdown.markdown(story_text)}
    </div>
    
    <div class="section">
        <h2>📱 פוסט סושיאל</h2>
        {markdown.markdown(post_text)}
        
        <h3>🎨 פרומפט ליצירת תמונה (Imagen)</h3>
        <p><i>הערה: יצירת תמונה אוטומטית הושעתה זמנית עקב מגבלות API של Google. השתמש בפרומפט זה במחולל תמונות:</i></p>
        <div class="prompt-box">{img_prompt}</div>
    </div>
</body>
</html>"""

        insights_path = actual_md_path.replace('.md', '_AI_Insights.html')
        with open(insights_path, 'w', encoding='utf-8') as html_f:
            html_f.write(html_content)
            
        print("   - מעלה קובץ תובנות מאוחד ל-Drive...")
        upload_callback(drive_svc, insights_path, target_category_folder_id, 'text/html')
            
    except Exception as ai_e:
        print(f"   ⚠️ שגיאה בשרשרת ה-AI: {ai_e}")
