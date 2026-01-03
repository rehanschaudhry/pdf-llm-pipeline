from src.app.gdrive_storage import GoogleDriveStorage
from src.app.pdf_processor import PDFProcessor
from src.app.parquet_creator import ParquetCreator
from src.app.database import SessionLocal
from src.app.models import Document
from datetime import datetime
import os

class PDFPipeline:
    """
    Complete PDF processing pipeline
    Integrates: Google Drive + PDF Processing + PostgreSQL
    """
    
    def __init__(self):
        self.storage = GoogleDriveStorage()
        self.processor = PDFProcessor()
        self.parquet_creator = ParquetCreator()
        
        # Setup folders in Google Drive
        self.storage.setup_pipeline_folders()
    
    def process_document(self, pdf_path: str, filename: str = None):
        """
        Complete pipeline: Upload → Process → Track
        
        Args:
            pdf_path: Local path to PDF file
            filename: Name to use (defaults to original filename)
            
        Returns:
            Document object from database
        """
        print("\n" + "=" * 70)
        print("🚀 STARTING FULL PIPELINE")
        print("=" * 70)
        
        # Use original filename if not specified
        if not filename:
            filename = os.path.basename(pdf_path)
        
        file_size = os.path.getsize(pdf_path)
        
        # Database session
        db = SessionLocal()
        
        try:
            # Step 1: Create Document record
            print("\n📝 Step 1: Creating document record in PostgreSQL...")
            doc = Document(
                filename=filename,
                file_size=file_size,
                status="uploading"
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)
            print(f"✓ Document created (ID: {doc.id})")
            
            # Step 2: Upload to Google Drive (upload folder)
            print("\n☁️  Step 2: Uploading to Google Drive (upload/)...")
            upload_result = self.storage.upload_file(pdf_path, 'upload', filename)
            
            doc.gdrive_upload_id = upload_result['id']
            doc.current_folder = 'upload'
            doc.status = "uploaded"
            db.commit()
            print(f"✓ Uploaded (File ID: {upload_result['id']})")
            
            # Step 3: Move to staging
            print("\n📦 Step 3: Moving to staging...")
            self.storage.move_file(doc.gdrive_upload_id, 'upload', 'staging')
            
            doc.gdrive_staging_id = doc.gdrive_upload_id  # Same file, new location
            doc.current_folder = 'staging'
            doc.status = "staged"
            db.commit()
            print(f"✓ Moved to staging")
            
            # Step 4: Move to processing
            print("\n⚙️  Step 4: Moving to processing...")
            self.storage.move_file(doc.gdrive_staging_id, 'staging', 'processing')
            
            doc.gdrive_processing_id = doc.gdrive_staging_id
            doc.current_folder = 'processing'
            doc.status = "processing"
            db.commit()
            print(f"✓ Moved to processing")
            
            # Step 5: Process PDF
            print("\n🔧 Step 5: Processing PDF...")
            result = self.processor.process_pdf(pdf_path, chunk_size=500)
            
            if not result:
                doc.status = "failed"
                db.commit()
                print("✗ Processing failed!")
                return doc
            
            # Update document with processing results
            doc.page_count = result['page_count']
            doc.word_count = result['word_count']
            doc.chunk_count = result['chunk_count']
            db.commit()
            
            # Step 6: Create Parquet file
            print("\n📊 Step 6: Creating Parquet file...")
            parquet_filename = filename.replace('.pdf', '.parquet').replace('.txt', '.parquet')
            parquet_path = f"temp_{parquet_filename}"
            
            metadata = {
                'document_id': doc.id,
                'filename': filename,
                'page_count': result['page_count'],
                'word_count': result['word_count']
            }
            
            success = self.parquet_creator.create_parquet(
                result['chunks'],
                parquet_path,
                metadata
            )
            
            if not success:
                doc.status = "failed"
                db.commit()
                print("✗ Parquet creation failed!")
                return doc
            
            # Step 7: Upload Parquet to Google Drive
            print("\n☁️  Step 7: Uploading Parquet to Google Drive (parquet/)...")
            parquet_result = self.storage.upload_file(
                parquet_path,
                'parquet',
                parquet_filename
            )
            print(f"✓ Parquet uploaded (File ID: {parquet_result['id']})")
            
            # Clean up local parquet file
            if os.path.exists(parquet_path):
                os.remove(parquet_path)
            
            # Step 8: Move original PDF to processed
            print("\n✅ Step 8: Moving PDF to processed...")
            self.storage.move_file(doc.gdrive_processing_id, 'processing', 'processed')
            
            doc.gdrive_processed_id = doc.gdrive_processing_id
            doc.current_folder = 'processed'
            doc.status = "processed"
            doc.processed_at = datetime.now()
            db.commit()
            print(f"✓ Moved to processed")
            
            # Final summary
            print("\n" + "=" * 70)
            print("✅ PIPELINE COMPLETE!")
            print("=" * 70)
            print(f"Document ID: {doc.id}")
            print(f"Filename: {doc.filename}")
            print(f"Status: {doc.status}")
            print(f"Pages: {doc.page_count}")
            print(f"Words: {doc.word_count}")
            print(f"Chunks: {doc.chunk_count}")
            print(f"Upload ID: {doc.gdrive_upload_id}")
            print(f"Processed ID: {doc.gdrive_processed_id}")
            print(f"Parquet ID: {parquet_result['id']}")
            print(f"Current folder: {doc.current_folder}")
            print("\n📁 Check your Google Drive:")
            print(f"  - processed/ folder: {filename}")
            print(f"  - parquet/ folder: {parquet_filename}")
            print("=" * 70)
            
            return doc
            
        except Exception as e:
            print(f"\n✗ Pipeline error: {e}")
            if doc:
                doc.status = "failed"
                db.commit()
            raise
            
        finally:
            db.close()


def test_full_pipeline():
    """Test the complete integrated pipeline"""
    print("=" * 70)
    print("FULL PIPELINE INTEGRATION TEST")
    print("=" * 70)
    
    # Create test document
    print("\n📄 Creating test document...")
    test_content = """
    iPhone 15 Pro Complete Guide
    
    Introduction:
    The iPhone 15 Pro represents Apple's most advanced smartphone to date.
    With the A17 Pro chip, titanium design, and revolutionary camera system,
    this device sets new standards for mobile technology.
    
    Key Features:
    - A17 Pro chip with 6-core CPU
    - 48MP main camera with 5x telephoto
    - Titanium frame (lighter and stronger)
    - Action button (customizable control)
    - USB-C with USB 3 speeds
    - Always-On display with ProMotion
    - Up to 29 hours video playback
    
    Camera System Details:
    The triple camera system includes a 48MP main sensor, 12MP ultra-wide,
    and a 12MP telephoto with 5x optical zoom. Night mode, Deep Fusion, and
    Smart HDR 5 work together to capture stunning photos in any lighting.
    
    Performance:
    The A17 Pro chip delivers desktop-class performance in a mobile form factor.
    Ray tracing support enables console-quality gaming. The Neural Engine processes
    machine learning tasks instantly.
    
    Battery and Charging:
    All-day battery life supports up to 29 hours of video playback. Fast charging
    reaches 50% in 30 minutes with a 20W adapter. MagSafe provides 15W wireless
    charging with perfect alignment.
    """
    
    test_file = "test_complete_manual.txt"
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    print(f"✓ Created: {test_file}")
    
    # Run pipeline
    pipeline = PDFPipeline()
    doc = pipeline.process_document(test_file, "iphone_15_pro_manual.txt")
    
    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)
    
    print("\n✅ Full pipeline test complete!")
    print(f"Document {doc.id} processed successfully!")

if __name__ == "__main__":
    test_full_pipeline()