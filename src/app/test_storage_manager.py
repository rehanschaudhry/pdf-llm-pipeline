from src.app.gdrive_storage import GoogleDriveStorage
import tempfile
import os

def test_storage_manager():
    """Test the GoogleDriveStorage class"""
    print("=" * 60)
    print("GoogleDriveStorage Manager Test")
    print("=" * 60)
    
    # Initialize storage manager
    storage = GoogleDriveStorage()
    
    # 1. Setup folders
    print("\n1. Setting up pipeline folders...")
    folder_ids = storage.setup_pipeline_folders()
    
    # 2. Create a test file
    print("\n2. Creating test file...")
    test_content = "This is a test PDF for the pipeline!"
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(test_content)
        test_file = f.name
    
    print(f"✓ Created: {test_file}")
    
    # 3. Upload to 'upload' folder
    print("\n3. Uploading to upload/ folder...")
    file_info = storage.upload_file(test_file, 'upload', 'test_document.txt')
    file_id = file_info['id']
    
    # 4. List files in upload folder
    print("\n4. Listing files in upload/ folder...")
    files = storage.list_files_in_folder('upload')
    
    # 5. Move: upload → staging
    print("\n5. Moving file: upload/ → staging/...")
    storage.move_file(file_id, 'upload', 'staging')
    
    # 6. Move: staging → processing
    print("\n6. Moving file: staging/ → processing/...")
    storage.move_file(file_id, 'staging', 'processing')
    
    # 7. Move: processing → processed
    print("\n7. Moving file: processing/ → processed/...")
    storage.move_file(file_id, 'processing', 'processed')
    
    # 8. List files in processed folder
    print("\n8. Listing files in processed/ folder...")
    files = storage.list_files_in_folder('processed')
    
    # 9. Download file
    print("\n9. Downloading file...")
    download_path = "downloaded_test.txt"
    storage.download_file(file_id, download_path)
    
    # 10. Verify download
    print("\n10. Verifying download...")
    if os.path.exists(download_path):
        with open(download_path, 'r') as f:
            content = f.read()
            print(f"✓ Content: {content}")
    
    # Cleanup
    os.remove(test_file)
    os.remove(download_path)
    
    print("\n" + "=" * 60)
    print("✓ All storage manager tests passed!")
    print("=" * 60)
    print("\nCheck your Google Drive at: https://drive.google.com")
    print("You should see folders: upload, staging, processing, processed, parquet")

if __name__ == "__main__":
    test_storage_manager()