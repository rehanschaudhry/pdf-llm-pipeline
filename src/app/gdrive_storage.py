from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import os
import io

SCOOP = ['https://www.googleapis.com/auth/drive.file']

class GoogleDriveStorage:
    """
    Manages file storage in Google Drive
    Simulates blob storage operations (upload, download, move between folders)
    """

    def __init__(self, credentials_files='credentials.json', token_path='token.json'):
        """Initialize Google Drive storage manager"""
        self.credential_files = credentials_files
        self.token_path = token_path
        self.service = None
        self.folder_ids = {}

        self.authenticate()

    def authenticate(self):
        """Authenticate and create the Google Drive service"""
        creds = None
        
        """Load existing credentials"""
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOOP)
        
        """Get new credentials if none are available or they are invalid"""

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credential_files, SCOOP)
                creds = flow.run_local_server(port=0)
            
            #  Save credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
            
                    # Build Drive service
        self.service = build('drive', 'v3', credentials=creds)
        print("✓ Connected to Google Drive")

    def create_folder(self, folder_name, parent_id=None):
        """Create a folder in Google Drive"""
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        folder = self.service.files().create(
            body=file_metadata,
            fields='id, name'
        ).execute()
        
        print(f"✓ Created folder: {folder_name} (ID: {folder['id']})")
        return folder['id']
    
    def find_folder(self, folder_name):
        """Find a folder by name"""
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        
        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        files = results.get('files', [])
        
        if files:
            return files[0]['id']
        return None
    
    def get_or_create_folder(self, folder_name):
        """Get folder ID, create if doesn't exist"""
        # Check cache first
        if folder_name in self.folder_ids:
            return self.folder_ids[folder_name]
        
        # Try to find existing folder
        folder_id = self.find_folder(folder_name)
        
        # Create if not found
        if not folder_id:
            folder_id = self.create_folder(folder_name)
        
        # Cache it
        self.folder_ids[folder_name] = folder_id
        return folder_id
    
    def upload_file(self, file_path, folder_name, filename=None):
        """
        Upload a file to Google Drive folder
        
        Args:
            file_path: Local path to file
            folder_name: Name of folder in Drive
            filename: Name to use in Drive (defaults to original filename)
            
        Returns:
            dict with file info (id, name, size)
        """
        # Get folder ID
        folder_id = self.get_or_create_folder(folder_name)
        
        # Use original filename if not specified
        if not filename:
            filename = os.path.basename(file_path)
        
        # File metadata
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        
        # Upload file
        media = MediaFileUpload(file_path, resumable=True)
        
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, size, createdTime'
        ).execute()
        
        print(f"✓ Uploaded: {filename} to {folder_name}/ (ID: {file['id']})")
        
        return {
            'id': file['id'],
            'name': file['name'],
            'size': file.get('size', 0),
            'created_time': file.get('createdTime')
        }
    
    def download_file(self, file_id, destination_path):
            """
            Download a file from Google Drive
            
            Args:
                file_id: Google Drive file ID
                destination_path: Where to save the file locally
                
            Returns:
                True if successful, False otherwise
            """
            try:
                request = self.service.files().get_media(fileId=file_id)
                
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                
                # Save to file
                with open(destination_path, 'wb') as f:
                    f.write(fh.getvalue())
                
                print(f"✓ Downloaded file ID {file_id} to {destination_path}")
                return True
                
            except Exception as e:
                print(f"✗ Download failed: {e}")
                return False
            
    def move_file(self, file_id, source_folder, target_folder):
        """
        Move file from one folder to another
        
        Args:
            file_id: Google Drive file ID
            source_folder: Source folder name
            target_folder: Target folder name
            
        Returns:
            Updated file info
        """
        # Get folder IDs
        source_id = self.get_or_create_folder(source_folder)
        target_id = self.get_or_create_folder(target_folder)
        
        # Move file (remove from source, add to target)
        file = self.service.files().update(
            fileId=file_id,
            addParents=target_id,
            removeParents=source_id,
            fields='id, name, parents'
        ).execute()
        
        print(f"✓ Moved file {file_id} from {source_folder}/ to {target_folder}/")
        
        return file
    
    def list_files_in_folder(self, folder_name):
        """
        List all files in a folder
        
        Args:
            folder_name: Name of folder
            
        Returns:
            List of file dicts
        """
        folder_id = self.get_or_create_folder(folder_name)
        
        query = f"'{folder_id}' in parents and trashed=false"
        
        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, size, createdTime)'
        ).execute()
        
        files = results.get('files', [])
        
        print(f"✓ Found {len(files)} file(s) in {folder_name}/")
        
        return files
    
    def setup_pipeline_folders(self):
        """
        Create all pipeline folders
        
        Returns:
            dict mapping folder names to IDs
        """
        print("\n📁 Setting up pipeline folders...")
        
        folders = ['upload', 'staging', 'processing', 'processed', 'parquet']
        
        folder_ids = {}
        for folder in folders:
            folder_ids[folder] = self.get_or_create_folder(folder)
        
        print("✓ All pipeline folders ready!")
        return folder_ids