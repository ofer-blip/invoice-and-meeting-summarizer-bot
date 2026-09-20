import base64
from googleapiclient.discovery import build
import config

def get_gmail_service(creds):
    """Builds the Gmail API service."""
    return build('gmail', 'v1', credentials=creds)

def search_invoice_emails(service, query=config.GMAIL_SEARCH_QUERY_BASE, max_results=50):
    """Searches for emails matching the query and returns a list of message summaries."""
    try:
        result = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        messages = result.get('messages', [])
        return messages
    except Exception as e:
        print(f"Error searching Gmail: {e}")
        return []

def get_message_details(service, msg_id):
    """Gets details of a specific message including subject, sender, date, and attachments metadata."""
    try:
        message = service.users().messages().get(userId='me', id=msg_id).execute()
        payload = message.get('payload', {})
        headers = payload.get('headers', [])
        
        subject = ""
        sender = ""
        date = ""
        for header in headers:
            name = header.get('name', '').lower()
            if name == 'subject':
                subject = header.get('value', '')
            elif name == 'from':
                sender = header.get('value', '')
            elif name == 'date':
                date = header.get('value', '')
                
        return {
            'id': msg_id,
            'subject': subject,
            'sender': sender,
            'date': date,
            'payload': payload
        }
    except Exception as e:
        print(f"Error fetching message details for {msg_id}: {e}")
        return None

def download_attachment(service, msg_id, attachment_id):
    """Downloads a specific attachment by ID and returns the raw bytes."""
    try:
        attachment = service.users().messages().attachments().get(
            userId='me', messageId=msg_id, id=attachment_id
        ).execute()
        data = attachment.get('data')
        if data:
            return base64.urlsafe_b64decode(data.encode('UTF-8'))
    except Exception as e:
        print(f"Error downloading attachment {attachment_id}: {e}")
    return None

def extract_pdf_attachments(service, message_details):
    """Finds all PDF attachments in a message's payload and returns a list of dictionaries with filename, id, and data."""
    attachments = []
    payload = message_details.get('payload', {})
    
    def walk_parts(parts):
        for part in parts:
            filename = part.get('filename', '')
            mime_type = part.get('mimeType', '')
            body = part.get('body', {})
            attachment_id = body.get('attachmentId')
            
            if attachment_id and (mime_type == 'application/pdf' or filename.lower().endswith('.pdf')):
                # Download the attachment bytes
                file_bytes = download_attachment(service, message_details['id'], attachment_id)
                if file_bytes:
                    attachments.append({
                        'filename': filename,
                        'id': attachment_id,
                        'bytes': file_bytes
                    })
            
            if 'parts' in part:
                walk_parts(part['parts'])

    if 'parts' in payload:
        walk_parts(payload['parts'])
    elif 'body' in payload and payload.get('body', {}).get('attachmentId'):
        # Single part message with attachment
        filename = payload.get('filename', '')
        attachment_id = payload['body']['attachmentId']
        if filename.lower().endswith('.pdf'):
            file_bytes = download_attachment(service, message_details['id'], attachment_id)
            if file_bytes:
                attachments.append({
                    'filename': filename,
                    'id': attachment_id,
                    'bytes': file_bytes
                })
                
    return attachments

def get_email_body(message_details):
    """Recursively extracts the HTML (preferred) or plain text body of the email."""
    import base64
    payload = message_details.get('payload', {})
    
    def walk_body(part):
        mime_type = part.get('mimeType', '')
        body = part.get('body', {})
        data = body.get('data')
        
        # If it's a leaf part and contains data
        if data and mime_type == 'text/html':
            html_data = base64.urlsafe_b64decode(data.encode('UTF-8')).decode('utf-8', errors='ignore')
            return html_data, 'text/html'
            
        html_found = None
        text_found = None
        
        # Walk child parts
        if 'parts' in part:
            for subpart in part['parts']:
                res = walk_body(subpart)
                if res:
                    val, m_type = res
                    if m_type == 'text/html':
                        html_found = val
                    elif m_type == 'text/plain':
                        text_found = val
                        
        if html_found:
            return html_found, 'text/html'
        if text_found:
            return text_found, 'text/plain'
            
        # Fallback for simple message
        if data and mime_type == 'text/plain':
            text_data = base64.urlsafe_b64decode(data.encode('UTF-8')).decode('utf-8', errors='ignore')
            return text_data, 'text/plain'
            
        return None

    res = walk_body(payload)
    if res:
        return res # returns (body_text, mime_type)
    return "", "text/plain"

def send_summary_email(service, recipient_email, subject, html_content):
    """Sends an HTML email notification using Gmail API."""
    from email.mime.text import MIMEText
    import base64
    try:
        message = MIMEText(html_content, 'html', 'utf-8')
        message['to'] = recipient_email
        message['subject'] = subject
        
        # Base64 encode the message
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        body = {'raw': raw}
        
        # Send
        service.users().messages().send(userId='me', body=body).execute()
        return True
    except Exception as e:
        print(f"Error sending summary email: {e}")
        return False
