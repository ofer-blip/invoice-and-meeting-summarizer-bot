import sys, os
sys.path.insert(0, 'src')
import gmail_service, google_auth
creds = google_auth.get_google_credentials()
svc = gmail_service.get_gmail_service(creds)
open('test.md', 'w').write('hello')
print(gmail_service.send_summary_email(svc, 'ofer@ddialog.co.il', 'Test Attach', 'Test body', ['test.md']))
