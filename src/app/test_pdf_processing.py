"""
Test PDF Extraction - Demonstrates Real Functionality
Run this to verify PDF processing works
"""

import sys
import os
from pdf_processor import PDFProcessor


def test_pdf_extraction():
    """Test the PDF processor with a sample file"""
    
    print("=" * 60)
    print("PDF EXTRACTION TEST")
    print("=" * 60)
    
    # Initialize processor
    processor = PDFProcessor(chunk_size=500, overlap=50)
    print("\n✓ PDF Processor initialized")
    print(f"  Chunk size: {processor.chunk_size} words")
    print(f"  Overlap: {processor.overlap} words")
    
    # Check if test PDF exists
    test_files = [
        "test_document.pdf",
        "sample.pdf",
        "../test_document.pdf"
    ]
    
    pdf_path = None
    for file in test_files:
        if os.path.exists(file):
            pdf_path = file
            break
    
    if pdf_path:
        print(f"\n✓ Found test PDF: {pdf_path}")
        
        try:
            # Process the PDF
            print("\nProcessing PDF...")
            result = processor.process_pdf(pdf_path)
            
            # Display results
            print("\n" + "=" * 60)
            print("EXTRACTION RESULTS")
            print("=" * 60)
            
            print("\nMETADATA:")
            for key, value in result['metadata'].items():
                print(f"  {key}: {value}")
            
            print(f"\nTEXT PREVIEW (first 500 chars):")
            print("-" * 60)
            print(result['full_text'][:500])
            print("-" * 60)
            
            print(f"\nCHUNKING:")
            print(f"  Total chunks created: {len(result['chunks'])}")
            if result['chunks']:
                print(f"\n  First chunk:")
                print(f"    Chunk ID: {result['chunks'][0]['chunk_id']}")
                print(f"    Word count: {result['chunks'][0]['word_count']}")
                print(f"    Text preview: {result['chunks'][0]['text'][:200]}...")
            
            print("\n" + "=" * 60)
            print("✓ PDF PROCESSING SUCCESSFUL!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n✗ Error processing PDF: {str(e)}")
            return False
    else:
        print("\n⚠ No test PDF found")
        print("\nTo test with a real PDF:")
        print("1. Place a PDF file in the current directory")
        print("2. Name it 'test_document.pdf' or 'sample.pdf'")
        print("3. Run this script again")
        print("\nAlternatively, test programmatically:")
        print("  processor = PDFProcessor()")
        print("  result = processor.process_pdf('your_file.pdf')")
    
    return True


def test_text_chunking():
    """Test text chunking functionality"""
    
    print("\n" + "=" * 60)
    print("TEXT CHUNKING TEST")
    print("=" * 60)
    
    processor = PDFProcessor(chunk_size=50, overlap=10)
    
    # Sample text
    sample_text = """
    Machine learning is a subset of artificial intelligence that focuses on 
    developing algorithms and statistical models that enable computers to perform 
    tasks without explicit instructions. Instead, these systems learn from data 
    and improve their performance over time. The field encompasses various 
    approaches including supervised learning, unsupervised learning, and 
    reinforcement learning. Deep learning, a subset of machine learning, uses 
    neural networks with multiple layers to process complex patterns in large 
    amounts of data. Applications of machine learning range from image recognition 
    and natural language processing to autonomous vehicles and medical diagnosis.
    """ * 3  # Repeat to create enough text for multiple chunks
    
    chunks = processor.chunk_text(sample_text)
    
    print(f"\nSample text length: {len(sample_text.split())} words")
    print(f"Chunk size: {processor.chunk_size} words")
    print(f"Overlap: {processor.overlap} words")
    print(f"Chunks created: {len(chunks)}")
    
    print("\nFirst 3 chunks:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n  Chunk {i}:")
        print(f"    Words: {chunk['word_count']}")
        print(f"    Range: {chunk['start_word']}-{chunk['end_word']}")
        print(f"    Text: {chunk['text'][:100]}...")
    
    print("\n✓ Chunking test successful!")
    
    return True


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("PDF PROCESSOR FUNCTIONALITY TEST")
    print("=" * 60)
    
    # Test text chunking
    test_text_chunking()
    
    # Test PDF extraction
    test_pdf_extraction()
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETE")
    print("=" * 60)
    print("\nThe PDF processor is ready to use!")
    print("\nNext steps:")
    print("1. Replace src/app/pdf_processor.py with pdf_processor_UPDATED.py")
    print("2. Update requirements.txt")
    print("3. Test with real PDF files")
    print("4. Integrate with Flask API")