# System Architecture

## High-Level Overview
```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT                                   │
│                    (Browser / API Client)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/REST
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      FLASK REST API                              │
│                    (Port 5000)                                   │
│                                                                  │
│  Endpoints:                                                      │
│  • POST /upload          → Upload & process documents           │
│  • GET  /documents       → List all documents                   │
│  • GET  /documents/<id>  → Get document details                 │
│  • GET  /documents/<id>/status → Check processing status        │
└─────────┬──────────────────────────────────┬────────────────────┘
          │                                  │
          │                                  │
          ▼                                  ▼
┌─────────────────────┐           ┌──────────────────────┐
│   PDF PROCESSOR     │           │  STORAGE MANAGER     │
│                     │           │                      │
│  • Extract Text     │           │  • Upload Files      │
│  • Clean Text       │           │  • Download Files    │
│  • Chunk Text       │           │  • Move Files        │
│  • Create Parquet   │           │  • List Files        │
└──────────┬──────────┘           └──────────┬───────────┘
           │                                 │
           │                                 │
           ▼                                 ▼
┌──────────────────────┐           ┌─────────────────────┐
│   PARQUET CREATOR    │           │  GOOGLE DRIVE API   │
│                      │           │                     │
│  • DataFrame         │           │  Folders:           │
│  • Compression       │           │  • upload/          │
│  • Schema            │           │  • staging/         │
└──────────┬───────────┘           │  • processing/      │
           │                       │  • processed/       │
           │                       │  • parquet/         │
           │                       └─────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────┐
│          POSTGRESQL DATABASE                  │
│          (Docker Container)                   │
│                                               │
│  documents table:                             │
│  • id, filename, file_size                   │
│  • status, current_folder                    │
│  • gdrive_*_id (tracking)                    │
│  • page_count, word_count, chunk_count       │
│  • created_at, processed_at                  │
└──────────────────────────────────────────────┘
```

## Data Flow

### Upload & Processing Flow
```
1. Client Upload
   │
   └──> POST /upload with PDF file
        │
        ▼
2. Flask API Receives
   │
   ├──> Save temporarily
   │
   └──> Create DB record (status: "uploading")
        │
        ▼
3. Google Drive Upload
   │
   └──> Upload to upload/ folder
        │
        └──> Update DB (status: "uploaded", gdrive_upload_id)
             │
             ▼
4. Move Through Stages
   │
   ├──> upload/ → staging/     (status: "staged")
   │
   ├──> staging/ → processing/ (status: "processing")
   │
   └──> Update DB with each move
        │
        ▼
5. PDF Processing
   │
   ├──> Extract text (PyPDF2)
   │
   ├──> Clean text (regex)
   │
   ├──> Chunk text (500 words, 50 overlap)
   │
   └──> Update DB (page_count, word_count, chunk_count)
        │
        ▼
6. Parquet Creation
   │
   ├──> Convert chunks to DataFrame
   │
   ├──> Add metadata columns
   │
   ├──> Save as .parquet file
   │
   └──> Upload to parquet/ folder in Google Drive
        │
        ▼
7. Finalization
   │
   ├──> Move PDF: processing/ → processed/
   │
   └──> Update DB (status: "processed", processed_at timestamp)
        │
        ▼
8. Return Response
   │
   └──> JSON with document details
```

## Technology Stack

### Backend Services
- **Web Framework**: Flask 3.0
- **Database**: PostgreSQL 15 (Docker)
- **ORM**: SQLAlchemy 2.0
- **Cloud Storage**: Google Drive API v3

### Processing Libraries
- **PDF**: PyPDF2 3.0
- **Data**: Pandas 2.1, PyArrow 14.0
- **Text Processing**: Python re (regex)

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Virtual Environment**: Python venv
- **Authentication**: OAuth 2.0 (Google)

## Security Considerations

### Implemented
✅ OAuth 2.0 for Google Drive  
✅ Environment variables for sensitive data  
✅ .gitignore for credentials  
✅ SQL injection prevention (SQLAlchemy ORM)  
✅ File type validation  
✅ Temporary file cleanup  

### Production Recommendations
- Use environment variables for all secrets
- Implement rate limiting
- Add authentication to API endpoints
- Use HTTPS in production
- Implement file size limits
- Add virus scanning for uploads
- Use production-grade WSGI server (Gunicorn)

## Scalability

### Current Limitations
- Single-threaded processing
- Synchronous API (blocking)
- Local temporary storage

### Scale-Out Strategy
1. **Background Processing**: Celery + Redis for async tasks
2. **Load Balancing**: Multiple Flask instances behind nginx
3. **Database**: Connection pooling, read replicas
4. **Storage**: CDN for static files
5. **Caching**: Redis for frequent queries

## Monitoring & Observability

### Implemented
✅ Application logging (pipeline.log)  
✅ Status tracking in database  
✅ Error handling with try/except  

### Production Additions
- Application Performance Monitoring (APM)
- Error tracking (Sentry)
- Metrics (Prometheus + Grafana)
- Health check endpoints
- Request tracing

## Database Schema

### documents Table
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR NOT NULL,
    file_size INTEGER,
    status VARCHAR DEFAULT 'uploaded',
    
    -- Google Drive tracking
    gdrive_upload_id VARCHAR,
    gdrive_staging_id VARCHAR,
    gdrive_processing_id VARCHAR,
    gdrive_processed_id VARCHAR,
    current_folder VARCHAR,
    
    -- Document metadata
    page_count INTEGER,
    word_count INTEGER,
    chunk_count INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    processed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);
```

## File Structure
```
Google Drive:
├── upload/           # Initial upload location
├── staging/          # Pre-processing queue
├── processing/       # Currently being processed
├── processed/        # Completed PDFs
└── parquet/         # Chunked data for LLM

Local Storage:
├── data/postgres/   # PostgreSQL data volume
├── pipeline.log     # Application logs
└── temp_*/         # Temporary processing (auto-deleted)
```

## API Response Formats

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error description"
}
```

## Processing Status Flow
```
uploaded → staged → processing → processed
                         ↓
                    (on error)
                         ↓
                      failed
```