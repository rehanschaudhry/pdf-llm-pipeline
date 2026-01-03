from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import os
import io

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    """Get authenticated Google Drive service"""
    creds = None
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def create_test_file():
    """Create a test PDF-like text file"""
    test_content = """
    iPhone 15 Pro User Manual
    ==========================
    
    Chapter 1: Getting Started
    - Turn on your iPhone
    - Set up Face ID
    - Configure your settings
    
    Chapter 2: Features
    - Camera system
    - Battery life
    - Performance
    
    This is a test file for our PDF pipeline!
    """
    
    filename = "test_iphone_manual.txt"
    with open(filename, 'w') as f:
        f.write(test_content)
    
    print(f"✓ Created test file: {filename}")
    return filename

def upload_file(service, file_path):
    """Upload a file to Google Drive"""
    print(f"\n📤 Uploading {file_path}...")
    
    file_metadata = {
        'name': os.path.basename(file_path)
    }
    
    media = MediaFileUpload(file_path, resumable=True)
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name, size'
    ).execute()
    
    print(f"✓ Upload successful!")
    print(f"  File ID: {file.get('id')}")
    print(f"  File Name: {file.get('name')}")
    print(f"  File Size: {file.get('size')} bytes")
    
    return file

def list_files(service):
    """List all files in Drive"""
    print(f"\n📋 Listing files in Google Drive...")
    
    results = service.files().list(
        pageSize=10,
        fields="files(id, name, size, createdTime)"
    ).execute()
    
    files = results.get('files', [])
    
    if not files:
        print('  No files found.')
    else:
        print(f"✓ Found {len(files)} file(s):")
        for file in files:
            print(f"  - {file['name']} (ID: {file['id']})")
    
    return files

def download_file(service, file_id, destination):
    """Download a file from Google Drive"""
    print(f"\n📥 Downloading file {file_id}...")
    
    request = service.files().get_media(fileId=file_id)
    
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"  Download progress: {int(status.progress() * 100)}%")
    
    # Save to file
    with open(destination, 'wb') as f:
        f.write(fh.getvalue())
    
    print(f"✓ Downloaded to: {destination}")

def main():
    """Test Google Drive upload and download"""
    print("=" * 60)
    print("Google Drive Upload/Download Test")
    print("=" * 60)
    
    # Get Drive service
    service = get_drive_service()
    print("✓ Connected to Google Drive")
    
    # Create test file
    test_file = create_test_file()
    
    # Upload file
    uploaded_file = upload_file(service, test_file)
    file_id = uploaded_file['id']
    
    # List files
    list_files(service)
    
    # Download file
    download_destination = "downloaded_" + test_file
    download_file(service, file_id, download_destination)
    
    # Verify download
    print(f"\n✓ Verifying download...")
    if os.path.exists(download_destination):
        with open(download_destination, 'r') as f:
            content = f.read()
            print(f"  First 100 characters: {content[:100]}...")
    
    print("\n" + "=" * 60)
    print("✓ All operations completed successfully!")
    print("=" * 60)
    print(f"\nCheck your Google Drive: https://drive.google.com")
    print(f"You should see: {uploaded_file['name']}")

if __name__ == "__main__":
    main()