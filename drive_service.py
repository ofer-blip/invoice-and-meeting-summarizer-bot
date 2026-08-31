import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import config
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import re

def get_drive_service(creds):
    """Builds the Google Drive API service."""
    return build('drive', 'v3', credentials=creds)

def get_main_parent_folder_id(service):
    """Gets the main parent folder ID. If PARENT_FOLDER_ID is set in config, returns it.
    Otherwise, finds or creates a folder named config.MAIN_FOLDER_NAME in root and returns its ID."""
    if config.PARENT_FOLDER_ID:
        return config.PARENT_FOLDER_ID
        
    # Search for config.MAIN_FOLDER_NAME in the root of Google Drive
    query = f"mimeType = 'application/vnd.google-apps.folder' and name = '{config.MAIN_FOLDER_NAME}' and 'root' in parents and trashed = false"
    try:
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        if files:
            return files[0]['id']
            
        # Create it in root if not found
        file_metadata = {
            'name': config.MAIN_FOLDER_NAME,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': ['root']
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')
    except Exception as e:
        print(f"Error getting/creating main parent folder '{config.MAIN_FOLDER_NAME}': {e}")
        return None

def find_or_create_folder(service, folder_name, parent_id=None):
    """Finds a folder by name and parent, or creates it if it doesn't exist."""
    # Resolve the parent ID
    actual_parent_id = parent_id
    if actual_parent_id is None:
        actual_parent_id = get_main_parent_folder_id(service)
        
    query = f"mimeType = 'application/vnd.google-apps.folder' and name = '{folder_name}' and trashed = false"
    if actual_parent_id:
        query += f" and '{actual_parent_id}' in parents"
        
    try:
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        
        if files:
            return files[0]['id']
            
        # Create folder if not found
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if actual_parent_id:
            file_metadata['parents'] = [actual_parent_id]
            
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')
    except Exception as e:
        print(f"Error finding/creating folder '{folder_name}': {e}")
        return None

def upload_file_to_drive(service, file_name, file_bytes, folder_id, mime_type='application/pdf'):
    """Uploads bytes to a specific Google Drive folder."""
    try:
        # Check if file already exists in that folder to avoid duplicates
        query = f"name = '{file_name}' and '{folder_id}' in parents and trashed = false"
        results = service.files().list(q=query, fields="files(id)").execute()
        existing_files = results.get('files', [])
        
        if existing_files:
            print(f"File '{file_name}' already exists in Drive. Skipping upload.")
            return existing_files[0]['id']
            
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        
        media = MediaIoBaseUpload(
            io.BytesIO(file_bytes),
            mimetype=mime_type,
            resumable=True
        )
        
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return uploaded_file.get('id')
    except Exception as e:
        print(f"Error uploading file '{file_name}': {e}")
        return None

def organize_invoice_in_drive(service, classification, file_bytes, mime_type='application/pdf'):
    """Organizes the invoice into the correct month and category (הכנסות/הוצאות) folders."""
    # Extract year and month for folder naming (e.g. 2026-08)
    date_str = classification.document_date
    if len(date_str) >= 7 and date_str[4] == '-' and date_str[7] == '-':
        year_month = date_str[:7]
    else:
        # Fallback to general folder if date structure is weird
        year_month = "כללי"
        
    parent_folder_name = f"חשבוניות {year_month}"
    
    # 1. Create or get Month Folder
    month_folder_id = find_or_create_folder(service, parent_folder_name)
    if not month_folder_id:
        print("Failed to get or create month folder.")
        return None, year_month, None
        
    # 2. Create or get subfolder (הכנסות or הוצאות)
    direction_folder_name = classification.direction # 'הכנסה' or 'הוצאה'
    # Map to plural for folder names
    if direction_folder_name == 'הכנסה':
        subfolder_name = 'הכנסות'
    elif direction_folder_name == 'הוצאה':
        subfolder_name = 'הוצאות'
    else:
        subfolder_name = 'אחר'
        
    subfolder_id = find_or_create_folder(service, subfolder_name, parent_id=month_folder_id)
    if not subfolder_id:
        print(f"Failed to get or create subfolder: {subfolder_name}")
        return None, year_month, subfolder_name
        
    # 3. Format filename: YYYY-MM-DD_SupplierName_Amount_InvoiceNum.ext
    # Sanitise name to avoid issues
    clean_supplier = "".join(c for c in classification.supplier_name if c.isalnum() or c in " _-")
    clean_supplier = clean_supplier.strip().replace(" ", "_")
    
    ext = '.html' if mime_type == 'text/html' else '.pdf'
    formatted_filename = f"{classification.document_date}_{clean_supplier}_{classification.total_amount}_{classification.invoice_number}{ext}"
    
    # 4. Upload
    print(f"Uploading '{formatted_filename}' to Google Drive under '{parent_folder_name}/{subfolder_name}'...")
    file_id = upload_file_to_drive(service, formatted_filename, file_bytes, subfolder_id, mime_type=mime_type)
    return file_id, year_month, subfolder_name

def create_or_get_spreadsheet(drive_service, sheets_service, folder_id, year_month):
    """Finds or creates a Google Sheet named 'ריכוז חשבוניות YYYY-MM' in the given folder and ensures tabs exist."""
    sheet_name = f"ריכוז חשבוניות {year_month}"
    query = f"mimeType = 'application/vnd.google-apps.spreadsheet' and name = '{sheet_name}' and '{folder_id}' in parents and trashed = false"
    
    try:
        results = drive_service.files().list(q=query, fields="files(id)").execute()
        files = results.get('files', [])
        
        if files:
            spreadsheet_id = files[0]['id']
        else:
            # Create new spreadsheet in the folder
            file_metadata = {
                'name': sheet_name,
                'mimeType': 'application/vnd.google-apps.spreadsheet',
                'parents': [folder_id]
            }
            spreadsheet = drive_service.files().create(body=file_metadata, fields='id').execute()
            spreadsheet_id = spreadsheet.get('id')
            
        # Get metadata to see what sheets currently exist
        sheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        existing_sheets = sheet_metadata.get('sheets', [])
        existing_titles = [s['properties']['title'] for s in existing_sheets]
        
        requests = []
        if 'הכנסות' not in existing_titles:
            requests.append({'addSheet': {'properties': {'title': 'הכנסות'}}})
        if 'הוצאות' not in existing_titles:
            requests.append({'addSheet': {'properties': {'title': 'הוצאות'}}})
            
        if requests:
            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'requests': requests}
            ).execute()
            
        # Delete Sheet1 if it exists and we now have the required sheets
        sheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        existing_sheets = sheet_metadata.get('sheets', [])
        existing_titles = [s['properties']['title'] for s in existing_sheets]
        
        if 'הכנסות' in existing_titles and 'הוצאות' in existing_titles and 'Sheet1' in existing_titles:
            sheet1_id = None
            for s in existing_sheets:
                if s['properties']['title'] == 'Sheet1':
                    sheet1_id = s['properties']['sheetId']
                    break
            if sheet1_id is not None:
                sheets_service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body={'requests': [{'deleteSheet': {'sheetId': sheet1_id}}]}
                ).execute()
                
        return spreadsheet_id
    except Exception as e:
        print(f"Error creating/getting spreadsheet: {e}")
        return None

def update_spreadsheet_data(sheets_service, spreadsheet_id, category, rows_data):
    """Writes/updates rows in the specified category sheet ('הכנסות' or 'הוצאות')."""
    # Headers in Hebrew
    headers = [['תאריך', 'שם ספק/לקוח', 'מספר מסמך', 'סכום', 'מטבע', 'קישור לקובץ']]
    
    # Category title range (e.g. 'הכנסות!A1:F')
    range_name = f"{category}!A1:F"
    
    # Add Total row if we have data
    if rows_data:
        num_rows = len(rows_data)
        # Data rows start at 2 and go up to num_rows + 1
        total_row = ['סה"כ', '', '', f'=SUM(D2:D{num_rows+1})', '', '']
        all_rows = headers + rows_data + [total_row]
    else:
        all_rows = headers
        
    try:
        # Clear existing data first
        sheets_service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            body={}
        ).execute()
        
        # Update values
        body = {
            'values': all_rows
        }
        
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        print(f"Updated '{category}' sheet with {len(rows_data)} items (including Total row).")
    except Exception as e:
        print(f"Error updating sheet data: {e}")

def reverse_hebrew(text):
    """Reverses Hebrew characters in a string for simple RTL rendering in ReportLab canvas."""
    if not text:
        return ""
    # Simple check if there are Hebrew characters
    if any('\u0590' <= c <= '\u05ff' for c in text):
        words = text.split()
        reversed_words = []
        for word in words:
            if any('\u0590' <= c <= '\u05ff' for c in word):
                reversed_words.append(word[::-1])
            else:
                reversed_words.append(word)
        return " ".join(reversed_words[::-1])
    return text

def generate_pdf_from_email_body(classification, email_subject, email_sender, email_body_text=""):
    """Generates a clean PDF receipt containing invoice metadata and original email body text."""
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    
    # Register Arial font for Hebrew support on Windows
    font_name = 'Helvetica'
    font_bold_name = 'Helvetica-Bold'
    arial_path = r"C:\Windows\Fonts\arial.ttf"
    arial_bold_path = r"C:\Windows\Fonts\arialbd.ttf"
    if os.path.exists(arial_path):
        try:
            pdfmetrics.registerFont(TTFont('Arial', arial_path))
            font_name = 'Arial'
            if os.path.exists(arial_bold_path):
                pdfmetrics.registerFont(TTFont('Arial-Bold', arial_bold_path))
                font_bold_name = 'Arial-Bold'
            else:
                font_bold_name = 'Arial'
        except Exception:
            pass
            
    # Draw Title
    can.setFont(font_bold_name, 16)
    can.drawString(50, 750, reverse_hebrew("סיכום חשבונית / קבלה מתוך מייל (נוצר אוטומטית)"))
    can.line(50, 740, 550, 740)
    
    # Draw Box for metadata
    can.setFont(font_bold_name, 11)
    y = 710
    
    details = [
        ("ספק / מנפיק:", classification.supplier_name),
        ("לקוח / מקבל:", classification.client_name),
        ("תאריך מסמך:", classification.document_date),
        ("סכום כולל:", f"{classification.total_amount} {classification.currency}"),
        ("מספר מסמך:", classification.invoice_number),
        ("סיווג:", classification.direction),
        ("נושא המייל:", email_subject),
        ("שולח המייל:", email_sender),
    ]
    
    for label, val in details:
        lbl_rev = reverse_hebrew(label)
        val_rev = reverse_hebrew(str(val))
        can.setFont(font_bold_name, 11)
        can.drawString(50, y, lbl_rev)
        can.setFont(font_name, 11)
        can.drawString(200, y, val_rev)
        y -= 22
        
    y -= 15
    can.setFont(font_bold_name, 12)
    can.drawString(50, y, reverse_hebrew("תוכן המייל המקורי (חלקי):"))
    can.line(50, y-5, 550, y-5)
    y -= 25
    
    # Draw email body text (limit to 30 lines to fit first page cleanly)
    can.setFont(f"{font_name}", 9)
    if email_body_text:
        # Strip HTML tags if there are any
        clean_text = re.sub(r'<[^>]+>', '\n', email_body_text)
        lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
        for line in lines[:30]:
            if y < 50:
                break
            clean_line = line[:80]
            can.drawString(50, y, reverse_hebrew(clean_line))
            y -= 15
            
    can.save()
    return packet.getvalue()
