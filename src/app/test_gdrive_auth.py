from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

# Scopes - what permissions we need
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate():
    """Authenticate with Google Drive"""
    creds = None
    
    # Check if we have saved credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next time
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Build Drive service
    service = build('drive', 'v3', credentials=creds)
    
    print("✓ Authentication successful!")
    print("✓ Connected to Google Drive!")
    
    # Test - list files
    results = service.files().list(pageSize=10, fields="files(id, name)").execute()
    files = results.get('files', [])
    
    print(f"\n✓ Found {len(files)} files in your Drive:")
    for file in files:
        print(f"  - {file['name']}")
    
    return service

if __name__ == "__main__":
    print("=" * 50)
    print("Google Drive Authentication Test")
    print("=" * 50)
    authenticate()