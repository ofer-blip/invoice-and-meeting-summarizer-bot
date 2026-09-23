import os

def run_extended_pipeline(drive_svc, target_category_folder_id, actual_md_path, transcript_md_path, summary_text, upload_callback):
    """
    Runs the extended AI pipeline (Coach, Story, Social) and uploads the results to Google Drive.
    """
    try:
        import ai_coach
        import story_engine
        import social_generator
        
        transcript_text = ""
        if transcript_md_path and os.path.exists(transcript_md_path):
            with open(transcript_md_path, 'r', encoding='utf-8') as tf:
                transcript_text = tf.read()
                
        text_for_ai = transcript_text if transcript_text else summary_text
        
        print("   - מפעיל AI Coach (מאמן אישי)...")
        coach_report = ai_coach.generate_coach_report(text_for_ai)
        coach_path = actual_md_path.replace('.md', '_AI_Coach.md')
        with open(coach_path, 'w', encoding='utf-8') as cf:
            cf.write(coach_report)
        upload_callback(drive_svc, coach_path, target_category_folder_id, 'text/markdown')
        
        print("   - מפעיל Story Engine (מספר סיפורים)...")
        story_text = story_engine.generate_story(text_for_ai)
        story_path = actual_md_path.replace('.md', '_Story.md')
        with open(story_path, 'w', encoding='utf-8') as sf:
            sf.write(story_text)
        upload_callback(drive_svc, story_path, target_category_folder_id, 'text/markdown')
        
        print("   - מפעיל Social Generator (סושיאל)...")
        post_text, img_prompt = social_generator.generate_social_content(text_for_ai)
        social_path = actual_md_path.replace('.md', '_Social.md')
        with open(social_path, 'w', encoding='utf-8') as soc_f:
            soc_f.write(f"{post_text}\n\n--- Prompt ---\n{img_prompt}")
        upload_callback(drive_svc, social_path, target_category_folder_id, 'text/markdown')
        
        print("   - יוצר תמונה מלווה (Imagen 3)...")
        img_bytes = social_generator.generate_image(img_prompt)
        if img_bytes:
            img_path = actual_md_path.replace('.md', '_Image.jpg')
            with open(img_path, 'wb') as imf:
                imf.write(img_bytes)
            upload_callback(drive_svc, img_path, target_category_folder_id, 'image/jpeg')
            print("   ✓ תמונה נוצרה והועלתה בהצלחה.")
            
    except Exception as ai_e:
        print(f"   ⚠️ שגיאה בשרשרת ה-AI: {ai_e}")
