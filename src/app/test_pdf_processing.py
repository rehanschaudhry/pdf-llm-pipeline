from src.app.pdf_processor import PDFProcessor
from src.app.parquet_creator import ParquetCreator
import os

def create_test_pdf_text():
    """Create a text file simulating PDF content"""
    content = """
    iPhone 15 Pro User Manual
    
    Chapter 1: Introduction
    Welcome to your new iPhone 15 Pro. This device features the latest A17 Pro chip,
    delivering unprecedented performance and efficiency. The titanium design makes it
    lighter and more durable than ever before.
    
    Chapter 2: Camera System
    The iPhone 15 Pro features a revolutionary camera system with a 48MP main sensor.
    The telephoto lens offers 5x optical zoom, perfect for capturing distant subjects.
    Advanced computational photography ensures every shot looks professional.
    
    Chapter 3: Display
    The Super Retina XDR display with ProMotion technology offers a 120Hz refresh rate.
    The always-on display keeps important information visible at all times. Peak brightness
    reaches 2000 nits for outdoor visibility.
    
    Chapter 4: Battery Life
    All-day battery life with up to 29 hours of video playback. Fast charging supports
    up to 50% charge in 30 minutes with a 20W adapter. MagSafe wireless charging is faster
    and more convenient than ever.
    
    Chapter 5: Connectivity
    5G connectivity provides blazing-fast download speeds. Wi-Fi 6E support ensures the
    fastest wireless networking. Bluetooth 5.3 offers improved range and stability for
    your wireless accessories.
    """
    
    filename = "test_iphone_manual.txt"
    with open(filename, 'w') as f:
        f.write(content)
    
    print(f"✓ Created test file: {filename}")
    return filename

def test_pdf_processing():
    """Test the complete PDF processing pipeline"""
    print("=" * 70)
    print("PDF Processing Pipeline Test")
    print("=" * 70)
    
    # 1. Create test file
    print("\n1. Creating test document...")
    test_file = create_test_pdf_text()
    
    # 2. Initialize processor
    print("\n2. Initializing PDF processor...")
    processor = PDFProcessor()
    
    # 3. Process the file
    print("\n3. Processing document...")
    result = processor.process_pdf(test_file, chunk_size=100)
    
    if not result:
        print("✗ Processing failed!")
        return
    
    # 4. Show results
    print("\n4. Processing Results:")
    print(f"  Total words: {result['word_count']}")
    print(f"  Total chunks: {result['chunk_count']}")
    print(f"  First chunk preview: {result['chunks'][0]['text'][:100]}...")
    
    # 5. Create Parquet file
    print("\n5. Creating Parquet file...")
    parquet_creator = ParquetCreator()
    
    metadata = {
        'filename': 'test_iphone_manual.txt',
        'page_count': 1,
        'word_count': result['word_count']
    }
    
    parquet_path = "test_chunks.parquet"
    success = parquet_creator.create_parquet(
        result['chunks'],
        parquet_path,
        metadata
    )
    
    if not success:
        print("✗ Parquet creation failed!")
        return
    
    # 6. Read back and verify
    print("\n6. Reading Parquet file...")
    df = parquet_creator.read_parquet(parquet_path)
    
    if df is not None:
        print(f"\n✓ Verification successful!")
        print(f"  Loaded {len(df)} chunks from Parquet")
        print(f"  Columns: {list(df.columns)}")
        print(f"\n  Sample chunk:")
        print(f"    ID: {df.iloc[0]['chunk_id']}")
        print(f"    Words: {df.iloc[0]['word_count']}")
        print(f"    Text preview: {df.iloc[0]['text'][:100]}...")
    
    # 7. Get file info
    print("\n7. Parquet file info:")
    info = parquet_creator.get_parquet_info(parquet_path)
    print(f"  Total rows: {info['row_count']}")
    print(f"  Total columns: {info['column_count']}")
    print(f"  File size: {info['file_size']} bytes")
    
    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)
    if os.path.exists(parquet_path):
        os.remove(parquet_path)
    
    print("\n" + "=" * 70)
    print("✓ All PDF processing tests passed!")
    print("=" * 70)

if __name__ == "__main__":
    test_pdf_processing()