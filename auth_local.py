import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from google_auth_oauthlib.flow import InstalledAppFlow
import config
from google_auth import SCOPES

def main():
    flow = InstalledAppFlow.from_client_secrets_file(config.CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=0, open_browser=False)
    with open(config.TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())
    print('Token updated successfully!')

if __name__ == '__main__':
    main()
