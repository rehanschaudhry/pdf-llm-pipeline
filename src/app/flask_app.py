from flask import Flask, request, jsonify
from flask_cors import CORS
from src.app.pipeline_integrated import PDFPipeline
from src.app.database import SessionLocal
from src.app.models import Document
import os
import tempfile
import shutil
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize pipeline
pipeline = PDFPipeline()

@app.route('/')
def home():
    """API home - health check"""
    return jsonify({
        'status': 'running',
        'message': 'PDF Pipeline API',
        'version': '1.0',
        'endpoints': {
            'GET /': 'Health check',
            'GET /documents': 'List all documents',
            'GET /documents/<id>': 'Get specific document',
            'POST /upload': 'Upload and process PDF',
            'GET /documents/<id>/status': 'Check processing status'
        }
    })

@app.route('/documents', methods=['GET'])
def list_documents():
    """List all documents in database"""
    db = SessionLocal()
    
    try:
        # Query all documents
        documents = db.query(Document).order_by(Document.created_at.desc()).all()
        
        # Convert to dict
        docs_list = []
        for doc in documents:
            docs_list.append({
                'id': doc.id,
                'filename': doc.filename,
                'status': doc.status,
                'file_size': doc.file_size,
                'page_count': doc.page_count,
                'word_count': doc.word_count,
                'chunk_count': doc.chunk_count,
                'current_folder': doc.current_folder,
                'created_at': doc.created_at.isoformat() if doc.created_at else None,
                'processed_at': doc.processed_at.isoformat() if doc.processed_at else None
            })
        
        return jsonify({
            'success': True,
            'count': len(docs_list),
            'documents': docs_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
    finally:
        db.close()

@app.route('/documents/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    """Get specific document details"""
    db = SessionLocal()
    
    try:
        # Query document by ID
        doc = db.query(Document).filter(Document.id == doc_id).first()
        
        if not doc:
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404
        
        return jsonify({
            'success': True,
            'document': {
                'id': doc.id,
                'filename': doc.filename,
                'status': doc.status,
                'file_size': doc.file_size,
                'page_count': doc.page_count,
                'word_count': doc.word_count,
                'chunk_count': doc.chunk_count,
                'current_folder': doc.current_folder,
                'gdrive_upload_id': doc.gdrive_upload_id,
                'gdrive_processed_id': doc.gdrive_processed_id,
                'created_at': doc.created_at.isoformat() if doc.created_at else None,
                'processed_at': doc.processed_at.isoformat() if doc.processed_at else None
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
    finally:
        db.close()

@app.route('/documents/<int:doc_id>/status', methods=['GET'])
def get_document_status(doc_id):
    """Get processing status of a document"""
    db = SessionLocal()
    
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        
        if not doc:
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404
        
        return jsonify({
            'success': True,
            'document_id': doc.id,
            'filename': doc.filename,
            'status': doc.status,
            'current_folder': doc.current_folder,
            'progress': {
                'uploaded': doc.gdrive_upload_id is not None,
                'staged': doc.gdrive_staging_id is not None,
                'processing': doc.gdrive_processing_id is not None,
                'processed': doc.gdrive_processed_id is not None,
            },
            'metrics': {
                'page_count': doc.page_count,
                'word_count': doc.word_count,
                'chunk_count': doc.chunk_count
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
    finally:
        db.close()

@app.route('/upload', methods=['POST'])
def upload_document():
    """
    Upload and process a PDF document
    
    Expects: multipart/form-data with 'file' field
    Returns: Document details and processing status
    """
    logger.info("Upload request received")
    
    # Check if file is in request
    if 'file' not in request.files:
        logger.warning("Upload failed: No file provided")
        return jsonify({
            'success': False,
            'error': 'No file provided'
        }), 400
    
    file = request.files['file']
    
    # Check if filename is empty
    if file.filename == '':
        logger.warning("Upload failed: No file selected")
        return jsonify({
            'success': False,
            'error': 'No file selected'
        }), 400
    
    # Check file extension
    allowed_extensions = {'.pdf', '.txt'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        logger.warning(f"Upload failed: Invalid file type {file_ext}")
        return jsonify({
            'success': False,
            'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
        }), 400
    
    try:
        # Save uploaded file temporarily
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)
        
        logger.info(f"File received: {file.filename} ({os.path.getsize(temp_path)} bytes)")
        
        # Process through pipeline
        logger.info(f"Starting pipeline for: {file.filename}")
        doc = pipeline.process_document(temp_path, file.filename)
        
        # Clean up temp file
        shutil.rmtree(temp_dir)
        logger.info(f"Temporary files cleaned up")
        
        logger.info(f"Document {doc.id} processed successfully: {file.filename}")
        
        return jsonify({
            'success': True,
            'message': 'Document uploaded and processed successfully',
            'document': {
                'id': doc.id,
                'filename': doc.filename,
                'status': doc.status,
                'file_size': doc.file_size,
                'page_count': doc.page_count,
                'word_count': doc.word_count,
                'chunk_count': doc.chunk_count,
                'current_folder': doc.current_folder,
                'created_at': doc.created_at.isoformat() if doc.created_at else None,
                'processed_at': doc.processed_at.isoformat() if doc.processed_at else None
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Processing failed for {file.filename}: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Processing failed: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Starting PDF Pipeline API")
    print("=" * 60)
    print("API running at: http://localhost:5000")
    print("Try these endpoints:")
    print("  GET  http://localhost:5000/")
    print("  GET  http://localhost:5000/documents")
    print("  GET  http://localhost:5000/documents/4")
    print("  GET  http://localhost:5000/documents/4/status")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)