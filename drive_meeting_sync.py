import os
import io
import sys
import tempfile
import config
import google_auth
import drive_service
import gmail_service
import meeting_summarizer
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

def find_or_create_root_folder(service, folder_name):
    """Finds or creates a top-level folder in Google Drive."""
    query = f"mimeType = 'application/vnd.google-apps.folder' and name = '{folder_name}' and 'root' in parents and trashed = false"
    try:
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        if files:
            return files[0]['id']
            
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': ['root']
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')
    except Exception as e:
        print(f"שגיאה באיתור/יצירת תיקייה '{folder_name}': {e}")
        return None

def find_or_create_subfolder(service, parent_folder_id, subfolder_name):
    """Finds or creates a subfolder within a parent folder in Google Drive."""
    query = f"mimeType = 'application/vnd.google-apps.folder' and name = '{subfolder_name}' and '{parent_folder_id}' in parents and trashed = false"
    try:
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        if files:
            return files[0]['id']
            
        file_metadata = {
            'name': subfolder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id]
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')
    except Exception as e:
        print(f"שגיאה באיתור/יצירת תיקיית משנה '{subfolder_name}': {e}")
        return parent_folder_id

def download_drive_file_to_temp(service, file_id, file_name):
    """Downloads a file from Google Drive to a local temporary file."""
    temp_dir = tempfile.gettempdir()
    local_path = os.path.join(temp_dir, file_name)
    
    request = service.files().get_media(fileId=file_id)
    with open(local_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"   הורדת קובץ מ-Drive: {int(status.progress() * 100)}%...")
                
    return local_path

def upload_local_file_to_drive(service, local_path, target_folder_id, mime_type='text/html'):
    """Uploads a local file to a Google Drive folder."""
    file_name = os.path.basename(local_path)
    file_metadata = {
        'name': file_name,
        'parents': [target_folder_id]
    }
    
    with open(local_path, 'rb') as f:
        media = MediaIoBaseUpload(f, mimetype=mime_type, resumable=True)
        uploaded = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
    return uploaded

def move_file_to_folder(service, file_id, source_folder_id, dest_folder_id):
    """Moves a file from one folder to another in Google Drive."""
    try:
        service.files().update(
            fileId=file_id,
            addParents=dest_folder_id,
            removeParents=source_folder_id,
            fields='id, parents'
        ).execute()
        return True
    except Exception as e:
        print(f"שגיאה בהעברת הקובץ לארכיון: {e}")
        return False

def sync_and_process_recordings():
    print("=" * 60)
    print("מתחיל סנכרון הקלטות מ-Google Drive ועיבוד סיכומים אוטומטי")
    print("=" * 60)
    
    # Authenticate Google
    creds = google_auth.get_google_credentials()
    drive_svc = drive_service.get_drive_service(creds)
    gmail_svc = gmail_service.get_gmail_service(creds)
    
    # Resolve folders in Google Drive
    print("\n1. מאמת תיקיות ב-Google Drive...")
    input_folder_id = find_or_create_root_folder(drive_svc, config.DRIVE_MEETINGS_INPUT_FOLDER)
    output_folder_id = find_or_create_root_folder(drive_svc, config.DRIVE_MEETINGS_OUTPUT_FOLDER)
    archive_folder_id = find_or_create_root_folder(drive_svc, config.DRIVE_MEETINGS_ARCHIVE_FOLDER)
    
    print(f"   ✓ תיקיית קליטת הקלטות: '{config.DRIVE_MEETINGS_INPUT_FOLDER}'")
    print(f"   ✓ תיקיית סיכומי פגישות: '{config.DRIVE_MEETINGS_OUTPUT_FOLDER}'")
    print(f"   ✓ תיקיית ארכיון: '{config.DRIVE_MEETINGS_ARCHIVE_FOLDER}'")
    
    # Query files in input folder
    query = f"'{input_folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder' and trashed = false"
    results = drive_svc.files().list(
        q=query, 
        fields="files(id, name, size, mimeType, createdTime)"
    ).execute()
    
    files = results.get('files', [])
    if not files:
        print(f"\n📂 לא נמצאו הקלטות חדשות בתיקיית '{config.DRIVE_MEETINGS_INPUT_FOLDER}' ב-Drive.")
        print("טיפ: שתף הקלטה מהטלפון ישירות לתיקייה זו כדי להפיק סיכום אוטומטי.")
        return
        
    print(f"\nנמצאו {len(files)} הקלטות לעיבוד:")
    for i, f in enumerate(files, 1):
        size_mb = int(f.get('size', 0)) / (1024 * 1024)
        print(f"  {i}. {f['name']} ({size_mb:.2f} MB)")
        
    # Process each recording
    processed_count = 0
    for idx, f in enumerate(files, 1):
        file_id = f['id']
        file_name = f['name']
        
        print("\n" + "-" * 50)
        print(f"[{idx}/{len(files)}] מעבד הקלטה: {file_name}...")
        
        temp_file_path = None
        try:
            # 1. Download recording
            temp_file_path = download_drive_file_to_temp(drive_svc, file_id, file_name)
            
            # 2. Summarize with Gemini
            html_output_path = meeting_summarizer.summarize_audio_file(temp_file_path, display_name=file_name)
            if not html_output_path:
                print(f"❌ דילוג על {file_name} עקב שגיאה בסיכום.")
                continue
                
            md_output_path = html_output_path.replace('.html', '.md')
            category = getattr(html_output_path, 'category', 'גפ\"ן')
            subfolder_name = config.DRIVE_MEETINGS_SUBFOLDER_BUSINESS if category == 'עסקים' else config.DRIVE_MEETINGS_SUBFOLDER_GEFEN
            
            # 3. Upload summary HTML & Markdown to Drive output folder inside category subfolder
            print(f"\n3. מעלה את הסיכום ל-Google Drive (תיקיית '{subfolder_name}')...")
            target_category_folder_id = find_or_create_subfolder(drive_svc, output_folder_id, subfolder_name)
            uploaded_html = upload_local_file_to_drive(drive_svc, html_output_path, target_category_folder_id, 'text/html')
            if os.path.exists(md_output_path):
                upload_local_file_to_drive(drive_svc, md_output_path, target_category_folder_id, 'text/markdown')
                
            print(f"   ✓ הסיכום נשמר ב-Drive בתיקיית '{config.DRIVE_MEETINGS_OUTPUT_FOLDER}/{subfolder_name}'")
            
            # 4. Move original audio file to archive folder in Drive
            print("\n4. מעביר את קובץ ההקלטה המקורי לארכיון ב-Drive...")
            move_file_to_folder(drive_svc, file_id, input_folder_id, archive_folder_id)
            print("   ✓ הקובץ הועבר בהצלחה לארכיון.")
            
            # 5. Send Email with Summary
            print("\n5. שולח מייל עם הסיכום המלא...")
            with open(html_output_path, 'r', encoding='utf-8') as hf:
                html_body = hf.read()
                
            recipient = config.NOTIFICATION_EMAIL_RECIPIENT.strip()
            if not recipient:
                # Default to user's own gmail
                profile = gmail_svc.users().getProfile(userId='me').execute()
                recipient = profile.get('emailAddress', 'me')
                
            subject = f"סיכום פגישה: {file_name}"
            email_sent = gmail_service.send_summary_email(gmail_svc, recipient, subject, html_body)
            if email_sent:
                print(f"   ✓ המייל נשלח בהצלחה אל: {recipient}")
            else:
                print(f"   ⚠️ לא ניתן היה לשלוח מייל אל {recipient}.")
                
            processed_count += 1
            print(f"🎉 סיום עיבוד בהצלחה עבור: {file_name}")
            
        except Exception as e:
            print(f"❌ שגיאה בעיבוד {file_name}: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception:
                    pass
                    
    print("\n" + "=" * 60)
    print(f"סיום סנכרון: עובדו בהצלחה {processed_count} מתוך {len(files)} הקלטות.")
    print("=" * 60)

if __name__ == "__main__":
    try:
        sync_and_process_recordings()
    except Exception as e:
        print(f"\n❌ שגיאה כללית בסנכרון: {e}")
        import traceback
        traceback.print_exc()
        if sys.stdin and sys.stdin.isatty():
            try:
                input("\nלחץ Enter לסגירה...")
            except (EOFError, KeyboardInterrupt):
                pass
