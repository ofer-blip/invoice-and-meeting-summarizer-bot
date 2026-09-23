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

_sync_in_progress = False

def sync_all_users(force_category=None):
    """Loops through all active clients in Firestore and syncs their recordings."""
    global _sync_in_progress
    if _sync_in_progress:
        print("⚠️ סנכרון כבר רץ ברקע. ממתין לסיום הריצה הנוכחית כדי למנוע כפילות.")
        import time
        while _sync_in_progress:
            time.sleep(2)
        return
        
    _sync_in_progress = True
    total_processed = 0
    total_found = 0
    try:
        print("=" * 60)
        print("מתחיל סנכרון רב-משתמשים (SaaS)")
        print("=" * 60)
        
        users = google_auth.get_all_active_users()
        if not users:
            print("לא נמצאו משתמשים פעילים במערכת.")
            return 0, 0
            
        for email in users:
            print(f"\n[{email}] מתחיל סנכרון...")
            creds = google_auth.get_credentials_for_user(email)
            if not creds:
                print(f"[{email}] ⚠️ שגיאה בטעינת הרשאות.")
                continue
            try:
                found, processed = sync_and_process_recordings(creds, email, force_category=force_category)
                total_found += found
                total_processed += processed
            except Exception as e:
                print(f"[{email}] ❌ שגיאה כללית: {e}")
                import traceback
                traceback.print_exc()
    finally:
        _sync_in_progress = False
    return total_found, total_processed

def sync_and_process_recordings(creds=None, user_email="Local User", force_category=None):
    print("\n" + "=" * 60)
    print(f"עיבוד עבור משתמש: {user_email}")
    print("=" * 60)
    
    # Authenticate Google
    if not creds:
        creds = google_auth.get_google_credentials()
    drive_svc = drive_service.get_drive_service(creds)
    gmail_svc = gmail_service.get_gmail_service(creds)
    
    # Fetch User Categories
    categories = []
    if user_email and user_email != "Local User":
        categories = google_auth.get_user_categories(user_email)
    
    if not categories:
        categories = ["כללי"]
    
    print(f"\nקטגוריות משתמש לניתוב: {categories}")
    
    # Resolve folders in Google Drive
    print("\n1. מאמת תיקיות ב-Google Drive...")
    input_folder_id = find_or_create_root_folder(drive_svc, config.DRIVE_MEETINGS_INPUT_FOLDER)
    output_folder_id = find_or_create_root_folder(drive_svc, config.DRIVE_MEETINGS_OUTPUT_FOLDER)
    archive_folder_id = find_or_create_root_folder(drive_svc, config.DRIVE_MEETINGS_ARCHIVE_FOLDER)
    
    # Ensure category subfolders exist in both INPUT and OUTPUT
    input_subfolders = {}
    for cat in categories:
        cat_name = cat if isinstance(cat, str) else cat.get("name", "כללי")
        if not cat_name:
            continue
        in_id = find_or_create_subfolder(drive_svc, input_folder_id, cat_name)
        if in_id:
            input_subfolders[in_id] = cat_name
        find_or_create_subfolder(drive_svc, output_folder_id, cat_name)
        
    print(f"   ✓ תיקיית קליטת הקלטות: '{config.DRIVE_MEETINGS_INPUT_FOLDER}'")
    print(f"   ✓ תיקיית סיכומי פגישות: '{config.DRIVE_MEETINGS_OUTPUT_FOLDER}'")
    print(f"   ✓ תיקיית ארכיון: '{config.DRIVE_MEETINGS_ARCHIVE_FOLDER}'")
    
    files_to_process = []
    
    # Query files in root input folder (Auto)
    query_root = f"'{input_folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder' and trashed = false"
    results_root = drive_svc.files().list(q=query_root, fields="files(id, name, size, mimeType, createdTime, parents)").execute()
    for f in results_root.get('files', []):
        mime_type = f.get('mimeType', '')
        if mime_type.startswith('image/') or mime_type.startswith('text/') or mime_type == 'application/pdf':
            print(f"   [Skipping] Non-media file found in root: {f.get('name')} ({mime_type})")
            continue
        f['manual_category'] = None
        files_to_process.append(f)
        
    # Query files in configured subfolders (Manual / Subfolder routing)
    scanned_folder_ids = set()
    for folder_id, cat_name in input_subfolders.items():
        scanned_folder_ids.add(folder_id)
        query_sub = f"'{folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder' and trashed = false"
        results_sub = drive_svc.files().list(q=query_sub, fields="files(id, name, size, mimeType, createdTime, parents)").execute()
        for f in results_sub.get('files', []):
            mime_type = f.get('mimeType', '')
            if mime_type.startswith('image/') or mime_type.startswith('text/') or mime_type == 'application/pdf':
                continue
            f['manual_category'] = cat_name
            files_to_process.append(f)
            
    # Fallback: Query files in any other unconfigured subfolders dynamically
    query_subfolders = f"'{input_folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    try:
        subfolders_results = drive_svc.files().list(q=query_subfolders, fields="files(id, name)").execute()
        for subfolder in subfolders_results.get('files', []):
            folder_id = subfolder['id']
            if folder_id in scanned_folder_ids:
                continue
                
            cat_name = subfolder['name']
            query_sub = f"'{folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder' and trashed = false"
            results_sub = drive_svc.files().list(q=query_sub, fields="files(id, name, size, mimeType, createdTime, parents)").execute()
            for f in results_sub.get('files', []):
                mime_type = f.get('mimeType', '')
                if mime_type.startswith('image/') or mime_type.startswith('text/') or mime_type == 'application/pdf':
                    continue
                f['manual_category'] = cat_name
                files_to_process.append(f)
    except Exception as e:
        print(f"Error querying dynamic subfolders: {e}")
            
    if not files_to_process:
        print(f"\n📂 לא נמצאו הקלטות חדשות לעיבוד.")
        return
        
    print(f"\nנמצאו {len(files_to_process)} הקלטות לעיבוד:")
    for i, f in enumerate(files_to_process, 1):
        size_mb = int(f.get('size', 0)) / (1024 * 1024)
        cat_str = f"[ניתוב אוטומטי]" if not f.get('manual_category') else f"[ניתוב ידני: {f.get('manual_category')}]"
        print(f"  {i}. {f['name']} ({size_mb:.2f} MB) {cat_str}")
        
    # Process each recording
    processed_count = 0
    for idx, f in enumerate(files_to_process, 1):
        file_id = f['id']
        file_name = f['name']
        manual_category = f.get('manual_category')
        if force_category and force_category != 'auto':
            manual_category = force_category
        parent_id = f.get('parents', [input_folder_id])[0]
        
        print("\n" + "-" * 50)
        print(f"[{idx}/{len(files_to_process)}] מעבד הקלטה: {file_name}...")
        
        temp_file_path = None
        try:
            # 1. Download recording
            temp_file_path = download_drive_file_to_temp(drive_svc, file_id, file_name)
            
            # --- Billing Check ---
            billing_info = google_auth.get_user_billing(user_email)
            if not billing_info['is_active']:
                print(f"❌ חשבון הלקוח {user_email} חסום. מדלג.")
                continue
                
            from tinytag import TinyTag
            try:
                tag = TinyTag.get(temp_file_path)
                duration_mins = (tag.duration or 60) / 60.0
            except:
                duration_mins = 1.0 # fallback
                
            if billing_info['minutes_used'] + duration_mins > billing_info['minutes_limit']:
                print(f"❌ חריגה ממכסת דקות ללקוח {user_email}. נוצלו: {billing_info['minutes_used']}/{billing_info['minutes_limit']}")
                # Send warning email if needed here
                continue
                
            print(f"   [Billing] משך הקובץ: {duration_mins:.1f} דקות. (יתרה לפני: {billing_info['minutes_limit'] - billing_info['minutes_used']:.1f} דק')")
            # --- End Billing Check ---
            
            # --- Early Archive (Locking Mechanism) ---
            print("\n  [נעילת קובץ] מעביר את הקובץ המקורי לארכיון ב-Drive לפני תחילת העיבוד כדי למנוע הרצה כפולה...")
            move_success = move_file_to_folder(drive_svc, file_id, parent_id, archive_folder_id)
            if not move_success:
                print(f"❌ הקובץ {file_name} לא הועבר לארכיון (ייתכן וכבר מעובד בתהליך מקביל). מדלג.")
                continue
            # ----------------------------------------
            
            # 2. Summarize with Gemini
            html_output_path = meeting_summarizer.summarize_audio_file(
                temp_file_path, 
                display_name=file_name,
                categories=categories,
                manual_category=manual_category
            )
            
            if not html_output_path:
                print(f"❌ דילוג על {file_name} עקב שגיאה בסיכום.")
                continue
                
            md_output_path = html_output_path.md_path
            
            # Resolve default category string
            def_cat = categories[0] if categories else "כללי"
            def_cat_str = def_cat if isinstance(def_cat, str) else def_cat.get("name", "כללי")
            category = getattr(html_output_path, 'category', def_cat_str)
            
            # 3. Upload summary HTML & Markdown to Drive output folder inside category subfolder
            print(f"\n3. מעלה את הסיכום ל-Google Drive (תיקיית '{category}')...")
            target_category_folder_id = find_or_create_subfolder(drive_svc, output_folder_id, category)
            # Support html_output_path being an object (as returned by updated summarize_audio_file)
            actual_html_path = getattr(html_output_path, 'html_path', str(html_output_path))
            actual_md_path = getattr(html_output_path, 'md_path', md_output_path)

            # HTML raw upload skipped based on user request
            # uploaded_html = upload_local_file_to_drive(drive_svc, actual_html_path, target_category_folder_id, 'text/html')
            if os.path.exists(actual_md_path):
                upload_local_file_to_drive(drive_svc, actual_md_path, target_category_folder_id, 'text/markdown')
                
            transcript_html_path = getattr(html_output_path, 'transcript_html_path', None)
            
            # Create Google Doc and PDF using Google Drive API (similar to Apps Script)
            print("   ממיר ל-Google Doc ול-PDF ושומר ב-Drive...")
            try:
                # Upload Summary HTML as Google Doc
                file_name_no_ext = os.path.splitext(os.path.basename(actual_html_path))[0]
                gdoc_metadata = {
                    'name': file_name_no_ext,
                    'parents': [target_category_folder_id],
                    'mimeType': 'application/vnd.google-apps.document'
                }
                with open(actual_html_path, 'rb') as hf:
                    gdoc_media = MediaIoBaseUpload(hf, mimetype='text/html', resumable=True)
                    gdoc_file = drive_svc.files().create(body=gdoc_metadata, media_body=gdoc_media, fields='id').execute()
                    gdoc_id = gdoc_file.get('id')
                
                # Export Summary Google Doc to PDF
                pdf_bytes = drive_svc.files().export(fileId=gdoc_id, mimeType='application/pdf').execute()
                
                # Upload Transcript HTML as Google Doc (if available)
                if transcript_html_path and os.path.exists(transcript_html_path):
                    print("   מעלה תמלול מלא ל-Drive כ-Google Doc...")
                    trans_file_name_no_ext = os.path.splitext(os.path.basename(transcript_html_path))[0]
                    t_gdoc_metadata = {
                        'name': trans_file_name_no_ext,
                        'parents': [target_category_folder_id],
                        'mimeType': 'application/vnd.google-apps.document'
                    }
                    with open(transcript_html_path, 'rb') as hf:
                        t_gdoc_media = MediaIoBaseUpload(hf, mimetype='text/html', resumable=True)
                        drive_svc.files().create(body=t_gdoc_metadata, media_body=t_gdoc_media, fields='id').execute()

                # 3c. Save Summary PDF locally (in case we want to attach to email later)
                pdf_output_path = actual_html_path.replace('.html', '.pdf')
                with open(pdf_output_path, 'wb') as pf:
                    pf.write(pdf_bytes)
                    
                # 3d. Upload PDF back to Drive
                pdf_metadata = {
                    'name': f"{file_name_no_ext}.pdf",
                    'parents': [target_category_folder_id]
                }
                pdf_media = MediaIoBaseUpload(io.BytesIO(pdf_bytes), mimetype='application/pdf', resumable=True)
                drive_svc.files().create(body=pdf_metadata, media_body=pdf_media, fields='id').execute()
                print("   ✓ קובצי Google Doc ו-PDF נוצרו ונשמרו בהצלחה ב-Drive.")
            except Exception as pdf_ex:
                print(f"   ⚠️ שגיאה ביצירת Doc/PDF: {pdf_ex}")
                
            print(f"   ✓ כל קובצי הסיכום נשמרו ב-Drive בתיקיית '{config.DRIVE_MEETINGS_OUTPUT_FOLDER}/{category}'")
            
            # (הקובץ המקורי כבר הועבר לארכיון בהתחלה כדי למנוע כפילויות)
            
            # 5. Send Email with Summary
            print("\n5. שולח מייל עם הסיכום המלא...")
            with open(actual_html_path, 'r', encoding='utf-8') as hf:
                html_body = hf.read()
            
            # Calculate remaining minutes after this run
            remaining_mins = max(0, billing_info['minutes_limit'] - billing_info['minutes_used'] - duration_mins)
            quota_msg = f'<div style="text-align: center; margin-top: 30px; padding: 15px; border-top: 1px solid #eee; font-family: Arial, sans-serif; font-size: 14px; color: #64748b; direction: rtl;">עד כה השתמשת ב-{billing_info["minutes_used"]:.0f} דקות. יתרת השימוש במנוי היא <strong>{remaining_mins:.0f} דקות</strong>.</div>'
            
            if '</body>' in html_body:
                html_body = html_body.replace('</body>', f'{quota_msg}\n</body>')
            else:
                html_body += quota_msg

                
            recipient = config.NOTIFICATION_EMAIL_RECIPIENT.strip()
            if not recipient:
                # Default to user's own gmail
                profile = gmail_svc.users().getProfile(userId='me').execute()
                recipient = profile.get('emailAddress', 'me')
                
            subject = f"סיכום פגישה: {file_name}"
            
            attachment_paths = []
            if os.path.exists(actual_md_path):
                attachment_paths.append(actual_md_path)
            
            # Use the local pdf file that was saved earlier
            if 'pdf_output_path' in locals() and os.path.exists(pdf_output_path):
                attachment_paths.append(pdf_output_path)
                
            transcript_md_path = getattr(html_output_path, 'transcript_md_path', None)
            if transcript_md_path and os.path.exists(transcript_md_path):
                attachment_paths.append(transcript_md_path)
                
            transcript_html_path = getattr(html_output_path, 'transcript_html_path', None)
            if transcript_html_path and os.path.exists(transcript_html_path):
                attachment_paths.append(transcript_html_path)
                
            email_sent = gmail_service.send_summary_email(gmail_svc, recipient, subject, html_body, attachment_paths)
            if email_sent:
                print(f"   ✓ המייל נשלח בהצלחה אל: {recipient} עם {len(attachment_paths)} קבצים מצורפים.")
            else:
                print(f"   ⚠️ לא ניתן היה לשלוח מייל אל {recipient}.")
                
            # Update billing usage
            google_auth.increment_user_minutes(user_email, duration_mins)
            
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
                    
    print("\\n" + "=" * 60)
    print(f"סיום סנכרון: עובדו בהצלחה {processed_count} מתוך {len(files_to_process)} הקלטות.")
    print("=" * 60)
    return len(files_to_process), processed_count

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
