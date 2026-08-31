import os

# Google API Credentials & Tokens
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')
TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'token.json')

# Base Gmail Search Query for Invoices (כולל מילים בעברית ובאנגלית, כולל אותיות יחס וספקים נפוצים)
GMAIL_SEARCH_QUERY_BASE = '(חשבונית OR קבלה OR תשלום OR חיוב OR רכישה OR החשבונית OR הקבלה OR התשלום OR החיוב OR הרכישה OR invoice OR receipt OR morning OR zoom OR billing OR payment OR "כביש 6" OR kvish6 OR from:google OR from:calmail)'

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

# Gemini API Configuration
# Make sure to set GEMINI_API_KEY environment variable, or configure it here.
GEMINI_API_KEY = 'AQ.Ab8RN6IL8JL8EC1V4LyOTMwZakgkenawg4RFmX7-0A5YMA0Gyg'
GEMINI_MODEL = 'gemini-2.5-flash'
