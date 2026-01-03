from src.app.gdrive_storage import GoogleDriveStorage
from src.app.parquet_creator import ParquetCreator
import pandas as pd

def view_parquet_from_drive():
    """Download and view Parquet file from Google Drive"""
    print("=" * 60)
    print("View Parquet File from Google Drive")
    print("=" * 60)
    
    # Initialize storage
    storage = GoogleDriveStorage()
    
    # List files in parquet folder
    print("\n📁 Files in parquet/ folder:")
    files = storage.list_files_in_folder('parquet')
    
    if not files:
        print("No parquet files found!")
        return
    
    # Get the first parquet file
    parquet_file = files[0]
    file_id = parquet_file['id']
    filename = parquet_file['name']
    
    print(f"\n📥 Downloading: {filename}")
    
    # Download to local
    local_path = f"temp_{filename}"
    storage.download_file(file_id, local_path)
    
    # Read and display
    print(f"\n📊 Reading Parquet file...")
    df = pd.read_parquet(local_path)
    
    print(f"\n✓ Parquet file contents:")
    print(f"  Rows: {len(df)}")
    print(f"  Columns: {list(df.columns)}")
    
    print(f"\n📋 Data preview:")
    print("="*60)
    
    # Show each chunk
    for idx, row in df.iterrows():
        print(f"\nChunk {row['chunk_id']}:")
        print(f"  Position: {row['position']}%")
        print(f"  Word count: {row['word_count']}")
        print(f"  Char count: {row['char_count']}")
        print(f"  Document ID: {row['doc_document_id']}")
        print(f"  Filename: {row['doc_filename']}")
        print(f"\n  Text preview (first 200 chars):")
        print(f"  {row['text'][:200]}...")
        print("-"*60)
    
    # Show full dataframe info
    print(f"\n📊 Full DataFrame Info:")
    print(df.info())
    
    # Cleanup
    import os
    if os.path.exists(local_path):
        os.remove(local_path)
        print(f"\n✓ Cleaned up temporary file")

if __name__ == "__main__":
    view_parquet_from_drive()