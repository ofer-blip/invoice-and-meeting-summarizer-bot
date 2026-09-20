import os

# Google API Credentials & Tokens
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')
TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'token.json')

# Base Gmail Search Query for Invoices (מדויק וללא רעשי התראות אבטחה של גוגל)
GMAIL_SEARCH_QUERY_BASE = '(חשבונית OR קבלה OR "דרישת תשלום" OR "אישור תשלום" OR "קבלה על תשלום" OR "פירוט חיוב" OR invoice OR receipt OR morning OR zoom OR billing OR "כביש 6" OR kvish6 OR from:avrech.com OR from:payments-noreply@google.com OR from:calmail OR from:invoices OR from:billing) -from:no-reply@accounts.google.com -from:calendar-notification@google.com -from:drive-shares-dm-noreply@google.com -from:googledevelopers-noreply@google.com'

# Email address to send the automated summary report to (can be Ofer's or Shahaf's email)
# If empty, it will default to the authenticated Gmail account itself (sending to self).
NOTIFICATION_EMAIL_RECIPIENT = ''

# Google Drive Target Folder for Invoices
# Set this to a specific folder ID if you want to upload inside a specific directory.
# If empty, a main folder with the name MAIN_FOLDER_NAME will be created automatically in the root of Google Drive.
PARENT_FOLDER_ID = ''
MAIN_FOLDER_NAME = 'חשבוניות'

# Google Drive Folders for Meetings & Recordings Automation
DRIVE_MEETINGS_INPUT_FOLDER = 'הקלטות לפגישות'
DRIVE_MEETINGS_OUTPUT_FOLDER = 'סיכומי פגישות'
DRIVE_MEETINGS_ARCHIVE_FOLDER = 'הקלטות שעובדו'
DRIVE_MEETINGS_SUBFOLDER_BUSINESS = 'עסקים'
DRIVE_MEETINGS_SUBFOLDER_GEFEN = 'גפ"ן'

# Master Meeting Summary Files on Local Machine
D_DIALOG_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER_BUSINESS_SUMMARY_FILE = os.path.join(D_DIALOG_ROOT, 'all_meetings_business.md')
MASTER_GEFEN_SUMMARY_FILE = os.path.join(D_DIALOG_ROOT, 'all_meeting_summaries.md')

# Gemini API Configuration
# Make sure to set GEMINI_API_KEY environment variable, or configure it here.
GEMINI_API_KEY = 'AQ.Ab8RN6IL8JL8EC1V4LyOTMwZakgkenawg4RFmX7-0A5YMA0Gyg'
GEMINI_MODEL = 'gemini-2.5-flash'
