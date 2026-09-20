import sys, os
sys.path.append('src')
from src.google_auth import get_google_credentials
from googleapiclient.discovery import build

creds = get_google_credentials()
svc = build('drive', 'v3', credentials=creds)

print("Folder ID details:")
try:
    f = svc.files().get(fileId='1YPBs1bZeLPxRXAJkJyec0QBBaw0ur6CU', fields='id, name').execute()
    print(f)
    print("Children:")
    children = svc.files().list(q="'1YPBs1bZeLPxRXAJkJyec0QBBaw0ur6CU' in parents and trashed=false", fields='files(id, name, mimeType)').execute()
    print(children)
except Exception as e:
    print(e)

print("\nRecent files:")
recent = svc.files().list(orderBy="createdTime desc", pageSize=10, fields='files(id, name, mimeType, parents)').execute()
print(recent)
