"""
Simple script to upload PDFs to your Flask API
Run this while Flask is running in another terminal
"""

import requests
import os

# Your PDF files
pdf_files = [
    "1706.03762v7.pdf",  # Transformer paper
    # Add your other PDFs here:
    # "gpt3.pdf",
    # "rag.pdf",
]

# Flask API URL
upload_url = "http://localhost:5000/upload"

print("=" * 60)
print("PDF UPLOAD TEST")
print("=" * 60)

for pdf_file in pdf_files:
    print(f"\nUploading: {pdf_file}")
    
    # Check if file exists
    if not os.path.exists(pdf_file):
        print(f"  ❌ File not found: {pdf_file}")
        continue
    
    try:
        # Open and upload the file
        with open(pdf_file, 'rb') as f:
            files = {'file': (pdf_file, f, 'application/pdf')}
            response = requests.post(upload_url, files=files)
        
        # Show response
        if response.status_code == 200:
            print(f"  ✅ Success!")
            result = response.json()
            print(f"  Response: {result}")
        else:
            print(f"  ❌ Error: {response.status_code}")
            print(f"  Message: {response.text}")
            
    except Exception as e:
        print(f"  ❌ Exception: {str(e)}")

print("\n" + "=" * 60)
print("UPLOAD TEST COMPLETE")
print("=" * 60)
