"""
PDF Processing Module - UPDATED with Real Extraction
Extracts text, metadata, and creates LLM-ready chunks from PDF files
"""

import PyPDF2
import re
from datetime import datetime
from typing import Dict, List, Tuple
import io


class PDFProcessor:
    """Processes PDF files to extract text and metadata"""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        """
        Initialize PDF processor
        
        Args:
            chunk_size: Number of words per chunk for LLM processing
            overlap: Number of words to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def extract_text_from_pdf(self, pdf_file_path: str) -> Tuple[str, Dict]:
        """
        Extract all text and metadata from a PDF file
        
        Args:
            pdf_file_path: Path to the PDF file
            
        Returns:
            Tuple of (full_text, metadata_dict)
        """
        try:
            with open(pdf_file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract metadata
                metadata = self._extract_metadata(pdf_reader)
                
                # Extract text from all pages
                full_text = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    full_text += page_text + "\n\n"
                
                # Clean the extracted text
                full_text = self._clean_text(full_text)
                
                # Add text statistics to metadata
                metadata['page_count'] = len(pdf_reader.pages)
                metadata['word_count'] = len(full_text.split())
                metadata['char_count'] = len(full_text)
                
                return full_text, metadata
                
        except Exception as e:
            raise Exception(f"Error extracting PDF: {str(e)}")
    
    def extract_text_from_bytes(self, pdf_bytes: bytes) -> Tuple[str, Dict]:
        """
        Extract text and metadata from PDF bytes (for uploaded files)
        
        Args:
            pdf_bytes: PDF file as bytes
            
        Returns:
            Tuple of (full_text, metadata_dict)
        """
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract metadata
            metadata = self._extract_metadata(pdf_reader)
            
            # Extract text from all pages
            full_text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                full_text += page_text + "\n\n"
            
            # Clean the extracted text
            full_text = self._clean_text(full_text)
            
            # Add text statistics to metadata
            metadata['page_count'] = len(pdf_reader.pages)
            metadata['word_count'] = len(full_text.split())
            metadata['char_count'] = len(full_text)
            
            return full_text, metadata
            
        except Exception as e:
            raise Exception(f"Error extracting PDF from bytes: {str(e)}")
    
    def _extract_metadata(self, pdf_reader: PyPDF2.PdfReader) -> Dict:
        """
        Extract metadata from PDF
        
        Args:
            pdf_reader: PyPDF2 reader object
            
        Returns:
            Dictionary of metadata
        """
        metadata = {}
        
        try:
            info = pdf_reader.metadata
            if info:
                metadata['title'] = info.get('/Title', 'Unknown')
                metadata['author'] = info.get('/Author', 'Unknown')
                metadata['subject'] = info.get('/Subject', 'Unknown')
                metadata['creator'] = info.get('/Creator', 'Unknown')
                metadata['producer'] = info.get('/Producer', 'Unknown')
                
                # Parse creation date if available
                creation_date = info.get('/CreationDate')
                if creation_date:
                    metadata['creation_date'] = self._parse_pdf_date(creation_date)
                else:
                    metadata['creation_date'] = None
        except:
            # If metadata extraction fails, use defaults
            metadata = {
                'title': 'Unknown',
                'author': 'Unknown',
                'subject': 'Unknown',
                'creator': 'Unknown',
                'producer': 'Unknown',
                'creation_date': None
            }
        
        return metadata
    
    def _parse_pdf_date(self, date_str: str) -> str:
        """
        Parse PDF date format to ISO format
        
        Args:
            date_str: PDF date string (format: D:YYYYMMDDHHmmSS)
            
        Returns:
            ISO formatted date string
        """
        try:
            # Remove 'D:' prefix if present
            if date_str.startswith('D:'):
                date_str = date_str[2:]
            
            # Extract date components
            year = int(date_str[0:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])
            
            return f"{year}-{month:02d}-{day:02d}"
        except:
            return "Unknown"
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might cause issues
        text = text.replace('\x00', '')
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def chunk_text(self, text: str) -> List[Dict]:
        """
        Split text into overlapping chunks for LLM processing
        
        Args:
            text: Full text to chunk
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        words = text.split()
        chunks = []
        
        if len(words) == 0:
            return chunks
        
        # Create overlapping chunks
        start = 0
        chunk_id = 0
        
        while start < len(words):
            # Get chunk of words
            end = start + self.chunk_size
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            
            # Create chunk dictionary
            chunk = {
                'chunk_id': chunk_id,
                'text': chunk_text,
                'word_count': len(chunk_words),
                'start_word': start,
                'end_word': min(end, len(words))
            }
            
            chunks.append(chunk)
            
            # Move to next chunk with overlap
            start = end - self.overlap
            chunk_id += 1
            
            # Prevent infinite loop if overlap >= chunk_size
            if start <= chunk_id * (self.chunk_size - self.overlap):
                start = chunk_id * (self.chunk_size - self.overlap)
        
        return chunks
    
    def process_pdf(self, pdf_path: str) -> Dict:
        """
        Complete PDF processing: extract text, metadata, and create chunks
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary containing text, metadata, and chunks
        """
        # Extract text and metadata
        full_text, metadata = self.extract_text_from_pdf(pdf_path)
        
        # Create chunks
        chunks = self.chunk_text(full_text)
        
        # Add chunk count to metadata
        metadata['chunk_count'] = len(chunks)
        
        return {
            'full_text': full_text,
            'metadata': metadata,
            'chunks': chunks,
            'processing_timestamp': datetime.now().isoformat()
        }
    
    def process_pdf_bytes(self, pdf_bytes: bytes) -> Dict:
        """
        Complete PDF processing from bytes: extract text, metadata, and create chunks
        
        Args:
            pdf_bytes: PDF file as bytes
            
        Returns:
            Dictionary containing text, metadata, and chunks
        """
        # Extract text and metadata
        full_text, metadata = self.extract_text_from_bytes(pdf_bytes)
        
        # Create chunks
        chunks = self.chunk_text(full_text)
        
        # Add chunk count to metadata
        metadata['chunk_count'] = len(chunks)
        
        return {
            'full_text': full_text,
            'metadata': metadata,
            'chunks': chunks,
            'processing_timestamp': datetime.now().isoformat()
        }


# Example usage and testing
if __name__ == "__main__":
    """Test the PDF processor"""
    
    processor = PDFProcessor(chunk_size=500, overlap=50)
    
    print("PDF Processor initialized successfully!")
    print(f"Chunk size: {processor.chunk_size} words")
    print(f"Overlap: {processor.overlap} words")
    print("\nReady to process PDF files.")
    print("\nUsage:")
    print("  result = processor.process_pdf('path/to/file.pdf')")
    print("  result = processor.process_pdf_bytes(pdf_bytes)")