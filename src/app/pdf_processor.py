import PyPDF2
import re
import os
from typing import List, Dict

class PDFProcessor:
    """Extract and process text from PDF files"""
    
    def __init__(self):
        pass
    
    def extract_text(self, pdf_path: str) -> str:
        """
        Extract all text from a PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text as string
        """
        print(f"📄 Extracting text from: {pdf_path}")
        
        text = ""
        
        try:
            with open(pdf_path, 'rb') as file:
                # Create PDF reader
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Get number of pages
                num_pages = len(pdf_reader.pages)
                print(f"  Found {num_pages} page(s)")
                
                # Extract text from each page
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    text += page_text + "\n"
                    
                print(f"✓ Extracted {len(text)} characters")
                
        except Exception as e:
            print(f"✗ Error extracting text: {e}")
            return ""
        
        return text
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        print(f"🧹 Cleaning text...")
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-\'\"]+', '', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        print(f"✓ Cleaned text: {len(text)} characters")
        
        return text
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict[str, any]]:
        """
        Split text into chunks for LLM processing
        
        Args:
            text: Text to chunk
            chunk_size: Target size of each chunk (in words)
            overlap: Number of words to overlap between chunks
            
        Returns:
            List of chunk dicts with text and metadata
        """
        print(f"✂️  Chunking text (chunk_size={chunk_size}, overlap={overlap})...")
        
        # Split into words
        words = text.split()
        
        chunks = []
        chunk_id = 0
        
        # Create chunks with overlap
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            # Calculate position percentage
            position = (i / len(words)) * 100 if len(words) > 0 else 0
            
            chunk = {
                'chunk_id': chunk_id,
                'text': chunk_text,
                'word_count': len(chunk_words),
                'char_count': len(chunk_text),
                'position': round(position, 2)
            }
            
            chunks.append(chunk)
            chunk_id += 1
        
        print(f"✓ Created {len(chunks)} chunks")
        
        return chunks
    
    def get_metadata(self, pdf_path: str) -> Dict[str, any]:
        """
        Extract metadata from PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dict with metadata
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                metadata = {
                    'page_count': len(pdf_reader.pages),
                    'title': pdf_reader.metadata.get('/Title', 'Unknown') if pdf_reader.metadata else 'Unknown',
                    'author': pdf_reader.metadata.get('/Author', 'Unknown') if pdf_reader.metadata else 'Unknown'
                }
                
                return metadata
                
        except Exception as e:
            print(f"✗ Error extracting metadata: {e}")
            return {
                'page_count': 0,
                'title': 'Unknown',
                'author': 'Unknown'
            }
    
    def process_pdf(self, pdf_path: str, chunk_size: int = 500) -> Dict[str, any]:
        """
        Complete PDF processing pipeline
        
        Args:
            pdf_path: Path to PDF file
            chunk_size: Size of text chunks
            
        Returns:
            Dict with processed data and metadata
        """
        print("\n" + "=" * 60)
        print(f"Processing PDF: {pdf_path}")
        print("=" * 60)
        
        # 1. Extract metadata
        metadata = self.get_metadata(pdf_path)
        
        # 2. Extract text
        raw_text = self.extract_text(pdf_path)
        
        if not raw_text:
            return None
        
        # 3. Clean text
        clean_text = self.clean_text(raw_text)
        
        # 4. Chunk text
        chunks = self.chunk_text(clean_text, chunk_size=chunk_size)
        
        # 5. Prepare result
        result = {
            'metadata': metadata,
            'raw_text': raw_text,
            'clean_text': clean_text,
            'chunks': chunks,
            'page_count': metadata['page_count'],
            'word_count': len(clean_text.split()),
            'chunk_count': len(chunks)
        }
        
        print("\n✓ PDF processing complete!")
        print(f"  Pages: {result['page_count']}")
        print(f"  Words: {result['word_count']}")
        print(f"  Chunks: {result['chunk_count']}")
        
        return result
    
    def extract_text(self, pdf_path: str) -> str:
        """
        Extract all text from a PDF file or text file
        
        Args:
            pdf_path: Path to PDF or text file
            
        Returns:
            Extracted text as string
        """
        print(f"📄 Extracting text from: {pdf_path}")
        
        text = ""
        
        try:
            # Check if it's a text file (for testing)
            if pdf_path.endswith('.txt'):
                with open(pdf_path, 'r', encoding='utf-8') as file:
                    text = file.read()
                print(f"✓ Extracted {len(text)} characters from text file")
                return text
            
            # Otherwise process as PDF
            with open(pdf_path, 'rb') as file:
                # Create PDF reader
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Get number of pages
                num_pages = len(pdf_reader.pages)
                print(f"  Found {num_pages} page(s)")
                
                # Extract text from each page
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    text += page_text + "\n"
                    
                print(f"✓ Extracted {len(text)} characters")
                
        except Exception as e:
            print(f"✗ Error extracting text: {e}")
            return ""
        
        return text
    
    def get_metadata(self, pdf_path: str) -> Dict[str, any]:
        """
        Extract metadata from PDF or estimate for text files
        
        Args:
            pdf_path: Path to PDF or text file
            
        Returns:
            Dict with metadata
        """
        try:
            # For text files, create basic metadata
            if pdf_path.endswith('.txt'):
                return {
                    'page_count': 1,
                    'title': os.path.basename(pdf_path),
                    'author': 'Test'
                }
            
            # For PDFs, extract real metadata
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                metadata = {
                    'page_count': len(pdf_reader.pages),
                    'title': pdf_reader.metadata.get('/Title', 'Unknown') if pdf_reader.metadata else 'Unknown',
                    'author': pdf_reader.metadata.get('/Author', 'Unknown') if pdf_reader.metadata else 'Unknown'
                }
                
                return metadata
                
        except Exception as e:
            print(f"✗ Error extracting metadata: {e}")
            return {
                'page_count': 0,
                'title': 'Unknown',
                'author': 'Unknown'
            }