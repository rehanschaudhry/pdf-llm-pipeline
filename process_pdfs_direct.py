"""
Direct PDF Processing - No Flask needed!
Processes PDFs and creates Parquet files directly
"""

from src.app.pdf_processor import PDFProcessor
import pandas as pd
import os

# Your PDF files (adjust names as needed)
pdf_files = [
    "1706.03762v7.pdf",  # Transformer paper
    "2005.11401v4.pdf",  # BERT paper
    "2005.14165v4.pdf"
    # "rag.pdf",
]

# Initialize processor
processor = PDFProcessor(chunk_size=500, overlap=50)

print("=" * 60)
print("DIRECT PDF PROCESSING")
print("=" * 60)

results = []

for pdf_file in pdf_files:
    print(f"\n{'='*60}")
    print(f"Processing: {pdf_file}")
    print('='*60)
    
    # Check if file exists
    if not os.path.exists(pdf_file):
        print(f"❌ File not found: {pdf_file}")
        print(f"   Looking in: {os.getcwd()}")
        continue
    
    try:
        # Process the PDF
        result = processor.process_pdf(pdf_file)
        
        # Show metadata
        print(f"\n📄 METADATA:")
        print(f"   Title: {result['metadata'].get('title', 'N/A')}")
        print(f"   Pages: {result['metadata']['page_count']}")
        print(f"   Words: {result['metadata']['word_count']}")
        print(f"   Chunks: {result['metadata']['chunk_count']}")
        
        # Show text preview
        print(f"\n📝 TEXT PREVIEW (first 300 chars):")
        print(f"   {result['full_text'][:300]}...")
        
        # Create Parquet file
        output_name = pdf_file.replace('.pdf', '_chunks.parquet')
        chunks_df = pd.DataFrame(result['chunks'])
        chunks_df.to_parquet(output_name, index=False)
        
        print(f"\n✅ SUCCESS!")
        print(f"   Parquet saved: {output_name}")
        print(f"   Chunks created: {len(result['chunks'])}")
        
        # Save result
        results.append({
            'filename': pdf_file,
            'pages': result['metadata']['page_count'],
            'words': result['metadata']['word_count'],
            'chunks': result['metadata']['chunk_count'],
            'parquet_file': output_name
        })
        
    except Exception as e:
        print(f"\n❌ ERROR processing {pdf_file}")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()

# Summary
print("\n" + "=" * 60)
print("PROCESSING COMPLETE")
print("=" * 60)

if results:
    print("\n📊 SUMMARY:")
    for r in results:
        print(f"\n✓ {r['filename']}")
        print(f"  Pages: {r['pages']} | Words: {r['words']} | Chunks: {r['chunks']}")
        print(f"  Output: {r['parquet_file']}")
    
    print(f"\n🎉 Successfully processed {len(results)} PDF(s)!")
    print("\n📁 Parquet files ready for LLM/RAG system!")
else:
    print("\n⚠️  No PDFs were processed successfully")
    print("\nTroubleshooting:")
    print("1. Make sure PDFs are in the same folder as this script")
    print("2. Check PDF filenames in the script match your actual files")
    print("3. Verify PyPDF2 is installed: pip install PyPDF2")
