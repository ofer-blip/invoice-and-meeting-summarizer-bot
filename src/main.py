import sys
import os
import argparse
from datetime import datetime, timedelta
import config
import google_auth
import gmail_service
import drive_service
import classifier

def safe_print(*args, **kwargs):
    """Safely prints arguments, replacing unencodable characters with '?' on Windows."""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or 'utf-8'
        new_args = []
        for arg in args:
            if isinstance(arg, str):
                new_args.append(arg.encode(encoding, errors='replace').decode(encoding))
            else:
                new_args.append(arg)
        print(*new_args, **kwargs)

def get_date_range_arguments():
    """Parses date arguments or defaults to the previous calendar month."""
    parser = argparse.ArgumentParser(description="Run the invoice sorting bot.")
    parser.add_argument('--month', type=int, help="Month to scan (1-12)")
    parser.add_argument('--year', type=int, help="Year to scan (e.g. 2026)")
    parser.add_argument('--start', type=str, help="Start date in YYYY/MM/DD format")
    parser.add_argument('--end', type=str, help="End date in YYYY/MM/DD format")
    
    args, unknown = parser.parse_known_args()
    
    start_date = None
    end_date = None
    
    if args.start and args.end:
        start_date = args.start
        end_date = args.end
    elif args.month or args.year:
        year = args.year if args.year else datetime.now().year
        month = args.month if args.month else datetime.now().month
        
        start_date = f"{year}/{month:02d}/01"
        if month == 12:
            next_month = 1
            next_year = year + 1
        else:
            next_month = month + 1
            next_year = year
        end_date = f"{next_year}/{next_month:02d}/01"
    else:
        # Default to previous calendar month
        now = datetime.now()
        first_of_this_month = now.replace(day=1)
        last_of_prev_month = first_of_this_month - timedelta(days=1)
        prev_month_year = last_of_prev_month.year
        prev_month = last_of_prev_month.month
        
        start_date = f"{prev_month_year}/{prev_month:02d}/01"
        end_date = f"{first_of_this_month.year}/{first_of_this_month.month:02d}/01"
        
    return start_date, end_date

def is_valid_document_date(doc_date_str, target_year, target_month):
    """Checks if the document date is within a reasonable range (up to 4 months before target, and not in the future)."""
    try:
        doc_date = datetime.strptime(doc_date_str, "%Y-%m-%d")
        target_date = datetime(target_year, target_month, 1)
        
        # 1. Check if date is in the future relative to the target month (allow up to 35 days after target start)
        if (doc_date - target_date).days > 35:
            return False
            
        # 2. Check if date is more than 4 months in the past relative to target_date
        min_date = target_date
        for _ in range(4):
            first_of_min = min_date.replace(day=1)
            min_date = (first_of_min - timedelta(days=1)).replace(day=1)
            
        if doc_date < min_date:
            return False
            
        return True
    except Exception:
        return False

def build_email_html(invoices_by_month, sheet_links):
    """Builds a beautiful RTL HTML body for the summary email."""
    html = """
    <div dir="rtl" style="font-family: Arial, sans-serif; direction: rtl; text-align: right; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
        <h2 style="color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 10px; margin-top: 0;">ריכוז חשבוניות חודשי - D-Dialog</h2>
        <p>היי,</p>
        <p>בוט החשבוניות סיים לעבד את המיילים ולהעלות את החשבוניות ל-Google Drive.</p>
        
        <h3 style="color: #333; margin-top: 20px;">ריכוז הדוחות שהופקו:</h3>
    """
    
    for ym, categories in invoices_by_month.items():
        link = sheet_links.get(ym, "#")
        html += f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 6px; margin-bottom: 15px; border-left: 4px solid #34a853;">
            <strong style="font-size: 16px; color: #202124;">חודש מס: {ym}</strong>
            <ul style="list-style-type: none; padding: 0; margin: 10px 0 10px 0;">
        """
        
        for cat_name, rows in categories.items():
            if rows:
                currency_totals = {}
                for r in rows:
                    try:
                        amt = float(r[3])
                        curr = r[4]
                        currency_totals[curr] = currency_totals.get(curr, 0) + amt
                    except ValueError:
                        continue
                
                totals_str = " + ".join([f"{val:,.2f} {curr}" for curr, val in currency_totals.items()])
                html += f"<li style='margin-bottom: 5px;'><strong>{cat_name}:</strong> {len(rows)} מסמכים (סה\"כ: {totals_str})</li>"
            else:
                html += f"<li style='margin-bottom: 5px; color: #70757a;'><strong>{cat_name}:</strong> לא נמצאו מסמכים</li>"
                
        if link != "#":
            html += f'<div style="margin-top: 10px;"><a href="{link}" style="color: #1a73e8; text-decoration: none; font-weight: bold;">[מעבר לקובץ גוגל שיטס המרכז]</a></div>'
        html += "</div>"
        
    html += """
        <p style="margin-top: 25px;">הדוחות והטבלאות המרכזות זמינים כעת בתיקיות ה-Google Drive המתאימות.</p>
        <p>בברכה,<br><strong>בוט החשבוניות של D-Dialog</strong></p>
    </div>
    """
    return html

def main():
    safe_print("=========================================")
    safe_print("בוט ניהול וריכוז חשבוניות - D-Dialog")
    safe_print("=========================================")
    
    # 1. Date Range Configuration
    start_date, end_date = get_date_range_arguments()
    
    # Extract target month and year for validation
    start_parts = start_date.split('/')
    target_year = int(start_parts[0])
    target_month = int(start_parts[1])
    
    # Expand date range for Gmail query:
    # 1 day before start to avoid timezone issues, and 15 days after target month end
    # because many suppliers (fuel, telecom, utilities) send previous month's invoice in early next month.
    try:
        start_dt = datetime.strptime(start_date, "%Y/%m/%d")
        end_dt = datetime.strptime(end_date, "%Y/%m/%d")
        gmail_start = (start_dt - timedelta(days=1)).strftime("%Y/%m/%d")
        gmail_end = (end_dt + timedelta(days=15)).strftime("%Y/%m/%d")
    except Exception:
        gmail_start = start_date
        gmail_end = end_date
        
    query = f"{config.GMAIL_SEARCH_QUERY_BASE} after:{gmail_start} before:{gmail_end}"
    
    # 2. Google Authentication
    try:
        safe_print("מתחבר לחשבון גוגל...")
        creds = google_auth.get_google_credentials()
        safe_print("התחברות לגוגל הצליחה.")
    except FileNotFoundError as e:
        safe_print(f"\nשגיאה: {e}")
        safe_print("אנא הנח את קובץ credentials.json בתיקיית העבודה והרץ שוב.")
        sys.exit(1)
    except Exception as e:
        safe_print(f"\nשגיאה במהלך ההתחברות: {e}")
        sys.exit(1)
        
    # Initialize Services
    gmail = gmail_service.get_gmail_service(creds)
    drive = drive_service.get_drive_service(creds)
    
    # 3. Initialize Gemini Client
    try:
        gemini_client = classifier.get_gemini_client()
        safe_print("חיבור ל-Gemini API הושלם בהצלחה.")
    except Exception as e:
        safe_print(f"\nשגיאה בחיבור ל-Gemini: {e}")
        safe_print("ודא שהגדרת את משתנה הסביבה GEMINI_API_KEY או הגדרת אותו בקובץ config.py.")
        sys.exit(1)
        
    # 4. Search Gmail for Invoice Emails
    safe_print(f"\nטווח סריקה: מ-{start_date} עד {end_date}")
    safe_print(f"מחפש הודעות מייל מתאימות...")
    emails = gmail_service.search_invoice_emails(gmail, query=query)
    
    if not emails:
        safe_print("לא נמצאו הודעות מייל מתאימות בטווח תאריכים זה.")
        return
        
    safe_print(f"נמצאו {len(emails)} הודעות מייל פוטנציאליות. מתחיל בעיבוד...")
    
    total_processed = 0
    total_uploaded = 0
    invoices_by_month = {}
    processed_keys = set()  # For deduplication: (date, supplier, amount)
    sheet_links = {}        # Track spreadsheet URLs by month
    
    for email_summary in emails:
        msg_id = email_summary['id']
        msg_details = gmail_service.get_message_details(gmail, msg_id)
        if not msg_details:
            continue
            
        safe_print(f"\nמעבד מייל: '{msg_details['subject']}' מאת: {msg_details['sender']}")
        
        # 1. Check for PDF attachments
        attachments = gmail_service.extract_pdf_attachments(gmail, msg_details)
        
        if attachments:
            safe_print(f"  נמצאו {len(attachments)} קבצי PDF במייל. מתחיל בניתוח בעזרת AI...")
            for att in attachments:
                total_processed += 1
                filename = att['filename']
                safe_print(f"  מנתח קובץ: '{filename}'...")
                
                # Use Gemini to classify PDF
                classification = classifier.classify_invoice(
                    gemini_client, 
                    att['bytes'], 
                    email_subject=msg_details['subject'], 
                    email_sender=msg_details['sender']
                )
                
                # Deduplication check on message + filename
                attachment_key = f"{msg_id}_{filename}"
                if attachment_key in processed_keys:
                    safe_print(f"    [דילוג כפילות] הקובץ '{filename}' כבר עובד עבור מייל זה.")
                    continue
                processed_keys.add(attachment_key)
                
                if not classification:
                    safe_print(f"    [חילוץ בסיסי] לא התקבל ניתוח מלא מ-AI עבור '{filename}', יוצר רשומה בסיסית.")
                    classification = classifier.InvoiceClassification(
                        is_invoice_or_receipt=True,
                        document_type="מסמך חשבונאי",
                        direction="לבדיקה",
                        supplier_name=msg_details.get('sender', 'ספק'),
                        document_date=f"{target_year}-{target_month:02d}-01",
                        total_amount=0.0,
                        invoice_number="0",
                        currency="ILS"
                    )
                    
                # Fix or fallback document date if missing or invalid
                if not classification.document_date or len(classification.document_date) < 8:
                    classification.document_date = f"{target_year}-{target_month:02d}-01"
                
                # Log details
                safe_print(f"    [מעבד מסמך] סוג: {classification.document_type}")
                safe_print(f"    ספק: {classification.supplier_name} | לקוח: {classification.client_name}")
                safe_print(f"    תאריך: {classification.document_date} | סכום: {classification.total_amount} {classification.currency}")
                safe_print(f"    סיווג: {classification.direction}")
                
                # Upload PDF to Google Drive directly in month folder
                target_ym = f"{target_year}-{target_month:02d}"
                file_id, year_month, category = drive_service.organize_invoice_in_drive(
                    drive, 
                    classification, 
                    att['bytes'], 
                    mime_type='application/pdf',
                    target_year_month=target_ym
                )
                if file_id:
                    safe_print(f"    [הצלחה] הקובץ הועלה לדרייב. מזהה קובץ: {file_id}")
                    total_uploaded += 1
                    
                    # Collect spreadsheet row data
                    drive_url = f"https://drive.google.com/file/d/{file_id}/view"
                    partner_name = classification.supplier_name if classification.direction == 'הוצאה' else (classification.client_name or classification.supplier_name)
                    row_data = [
                        classification.document_date,
                        partner_name,
                        classification.invoice_number,
                        classification.total_amount,
                        classification.currency,
                        drive_url
                    ]
                    
                    if target_ym not in invoices_by_month:
                        invoices_by_month[target_ym] = {'כל המסמכים': [], 'הכנסות': [], 'הוצאות': [], 'לבדיקה': []}
                        
                    invoices_by_month[target_ym]['כל המסמכים'].append(row_data)
                    if classification.direction == 'הכנסה':
                        invoices_by_month[target_ym]['הכנסות'].append(row_data)
                    elif classification.direction == 'הוצאה':
                        invoices_by_month[target_ym]['הוצאות'].append(row_data)
                    else:
                        invoices_by_month[target_ym]['לבדיקה'].append(row_data)
                else:
                    safe_print(f"    [שגיאה] העלאת הקובץ לדרייב נכשלה.")
        else:
            # 2. No attachments. Check email body text.
            safe_print("  לא נמצאו קבצי PDF. מנסה לנתח את גוף המייל עצמו כאישור תשלום/קבלה...")
            body_text, mime_type = gmail_service.get_email_body(msg_details)
            if not body_text:
                safe_print("  גוף המייל ריק או לא ניתן לקריאה.")
                continue
                
            body_key = f"{msg_id}_body"
            if body_key in processed_keys:
                safe_print(f"    [דילוג כפילות] גוף המייל עבור '{msg_details['subject']}' כבר עובד.")
                continue
            processed_keys.add(body_key)
            
            total_processed += 1
            classification = classifier.classify_invoice_body(
                gemini_client, 
                body_text, 
                email_subject=msg_details['subject'], 
                email_sender=msg_details['sender']
            )
            
            if not classification:
                safe_print(f"    [חילוץ בסיסי] לא התקבל ניתוח מלא מ-AI עבור גוף המייל, יוצר רשומה בסיסית.")
                classification = classifier.InvoiceClassification(
                    is_invoice_or_receipt=True,
                    document_type="אישור תשלום במייל",
                    direction="לבדיקה",
                    supplier_name=msg_details.get('sender', 'ספק'),
                    document_date=f"{target_year}-{target_month:02d}-01",
                    total_amount=0.0,
                    invoice_number="אישור",
                    currency="ILS"
                )
                
            if not classification.document_date or len(classification.document_date) < 8:
                classification.document_date = f"{target_year}-{target_month:02d}-01"
            
            # Log details
            safe_print(f"    [נמצאה הודעה פיננסית בגוף המייל] סוג: {classification.document_type}")
            safe_print(f"    ספק: {classification.supplier_name} | לקוח: {classification.client_name}")
            safe_print(f"    תאריך: {classification.document_date} | סכום: {classification.total_amount} {classification.currency}")
            safe_print(f"    סיווג: {classification.direction}")
            
            # Generate PDF from HTML body
            pdf_bytes = drive_service.generate_pdf_from_email_body(
                classification, 
                msg_details['subject'], 
                msg_details['sender'], 
                body_text
            )
            
            # Upload generated PDF to Google Drive directly in month folder
            target_ym = f"{target_year}-{target_month:02d}"
            file_id, year_month, category = drive_service.organize_invoice_in_drive(
                drive, 
                classification, 
                pdf_bytes, 
                mime_type='application/pdf',
                target_year_month=target_ym
            )
            
            if file_id:
                safe_print(f"    [הצלחה] קובץ ה-PDF עבור גוף המייל הועלה לדרייב. מזהה קובץ: {file_id}")
                total_uploaded += 1
                
                # Collect spreadsheet row data
                drive_url = f"https://drive.google.com/file/d/{file_id}/view"
                partner_name = classification.supplier_name if classification.direction == 'הוצאה' else (classification.client_name or classification.supplier_name)
                row_data = [
                    classification.document_date,
                    partner_name,
                    classification.invoice_number,
                    classification.total_amount,
                    classification.currency,
                    drive_url
                ]
                
                if target_ym not in invoices_by_month:
                    invoices_by_month[target_ym] = {'כל המסמכים': [], 'הכנסות': [], 'הוצאות': [], 'לבדיקה': []}
                    
                invoices_by_month[target_ym]['כל המסמכים'].append(row_data)
                if classification.direction == 'הכנסה':
                    invoices_by_month[target_ym]['הכנסות'].append(row_data)
                elif classification.direction == 'הוצאה':
                    invoices_by_month[target_ym]['הוצאות'].append(row_data)
                else:
                    invoices_by_month[target_ym]['לבדיקה'].append(row_data)
            else:
                safe_print(f"    [שגיאה] העלאת קובץ ה-PDF לדרייב נכשלה.")
                
    # Update Google Sheets with collected data
    if invoices_by_month:
        from googleapiclient.discovery import build as google_build
        try:
            safe_print("\nמעדכן קבצי גוגל שיטס לריכוז חשבוניות...")
            sheets = google_build('sheets', 'v4', credentials=creds)
            for ym, categories in invoices_by_month.items():
                parent_folder_name = f"חשבוניות {ym}"
                folder_id = drive_service.find_or_create_folder(drive, parent_folder_name)
                if folder_id:
                    spreadsheet_id = drive_service.create_or_get_spreadsheet(drive, sheets, folder_id, ym)
                    if spreadsheet_id:
                        for cat_name, rows in categories.items():
                            drive_service.update_spreadsheet_data(sheets, spreadsheet_id, cat_name, rows)
                        url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
                        sheet_links[ym] = url
                        safe_print(f"קובץ גוגל שיטס לריכוז החשבוניות זמין בכתובת: {url}")
            
            # Send Email Notification
            recipient = config.NOTIFICATION_EMAIL_RECIPIENT
            if not recipient:
                try:
                    profile = gmail.users().getProfile(userId='me').execute()
                    recipient = profile.get('emailAddress')
                except Exception:
                    recipient = ""
            
            if recipient:
                safe_print(f"\nשולח מייל סיכום אוטומטי אל: {recipient}...")
                email_subject = f"דו\"ח ריכוז חשבוניות חודשי ({start_date.split('/')[0]}/{start_date.split('/')[1]})"
                email_html = build_email_html(invoices_by_month, sheet_links)
                sent = gmail_service.send_summary_email(gmail, recipient, email_subject, email_html)
                if sent:
                    safe_print("מייל הסיכום נשלח בהצלחה!")
                else:
                    safe_print("שליחת מייל הסיכום נכשלה.")
                    
        except Exception as e:
            safe_print(f"שגיאה בעדכון גוגל שיטס או שליחת המייל: {e}")
                
    safe_print("\n=========================================")
    safe_print("הריצה הושלמה!")
    safe_print(f"סך הכל קבצים שנותחו: {total_processed}")
    safe_print(f"סך הכל קבצים שהועלו בהצלחה: {total_uploaded}")
    safe_print("=========================================")

if __name__ == '__main__':
    main()
