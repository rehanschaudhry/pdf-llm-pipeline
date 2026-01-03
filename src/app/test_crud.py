from src.app.database import SessionLocal
from src.app.models import Document
from datetime import datetime

def create_document():
    """Create a new document in the database."""
    # Open a new database session
    print("\n=== CREATE DOCUMENT ===")
    db = SessionLocal()

    # Create a new Document object
    doc = Document(
        filename="iphone_15_manual.pdf",
        file_size=2048000,
        status="uploaded"
    )

    # Add a session
    db.add(doc)

    # Save the document to the database
    db.commit()

    # Refresh to get auto-generated values (id, created_at
    db.refresh(doc)

    print(f"Created Document: {doc}")
    print(f"ID: {doc.id}")
    print(f"Status: {doc.status}")
    print(f"Created At: {doc.created_at}")  

    # Close the session
    db.close()

    return doc.id

def read_all_documents():
    """Read all documents from the database."""
    print("\n=== READ ALL ===")
    db = SessionLocal()

    # Query all documents
    documents = db.query(Document).all()
    
    print(f"Found {len(documents)} documents:")

    for doc in documents:
        print(f"ID: {doc.id}, Filename: {doc.filename}, File Size: {doc.file_size}, Status: {doc.status}, Created At: {doc.created_at}")
    db.close()
    return documents

def read_document_by_id(doc_id):
    """Read a specific document by ID"""
    print(f"\n=== READ DOCUMENT {doc_id} ===")
    
    db = SessionLocal()
    
    # Query by ID
    doc = db.query(Document).filter(Document.id == doc_id).first()
    
    if doc:
        print(f"✓ Found document:")
        print(f"  ID: {doc.id}")
        print(f"  Filename: {doc.filename}")
        print(f"  Size: {doc.file_size} bytes")
        print(f"  Status: {doc.status}")
        print(f"  Page count: {doc.page_count}")
        print(f"  Word count: {doc.word_count}")
        print(f"  Created: {doc.created_at}")
    else:
        print(f"✗ Document {doc_id} not found")
    
    db.close()
    return doc

def update_document(doc_id):
    """Update a document's fields"""
    print(f"\n=== UPDATE DOCUMENT {doc_id} ===")
    
    db = SessionLocal()
    
    # Find the document
    doc = db.query(Document).filter(Document.id == doc_id).first()
    
    if doc:
        # Update fields
        doc.status = "processing"
        doc.page_count = 250
        doc.word_count = 125000
        doc.chunk_count = 50
        
        # Save changes
        db.commit()
        
        print(f"✓ Updated document:")
        print(f"  New status: {doc.status}")
        print(f"  Pages: {doc.page_count}")
        print(f"  Words: {doc.word_count}")
        print(f"  Chunks: {doc.chunk_count}")
    else:
        print(f"✗ Document {doc_id} not found")
    
    db.close()

def delete_document(doc_id):
    """Delete a document from database"""
    print(f"\n=== DELETE DOCUMENT {doc_id} ===")
    
    db = SessionLocal()
    
    # Find document
    doc = db.query(Document).filter(Document.id == doc_id).first()
    
    if doc:
        db.delete(doc)
        db.commit()
        print(f"✓ Deleted document {doc_id}")
    else:
        print(f"✗ Document {doc_id} not found")
    
    db.close()

def main():
    """Test all CRUD operations"""
    print("=" * 60)
    print("CRUD OPERATIONS TEST - iPhone Manual Processing")
    print("=" * 60)
    
    # CREATE
    doc_id = create_document()
    
    # READ ALL
    read_all_documents()
    
    # READ ONE
    read_document_by_id(doc_id)
    
    # UPDATE
    update_document(doc_id)
    
    # READ AGAIN (see the updates)
    read_document_by_id(doc_id)
    
    # DELETE
    delete_document(doc_id)
    
    # READ ALL AGAIN (should be gone)
    read_all_documents()
    
    print("\n" + "=" * 60)
    print("✓ All CRUD operations completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()