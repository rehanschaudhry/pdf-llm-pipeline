# PDF Processing Pipeline

A complete end-to-end pipeline for processing PDF documents, extracting text, chunking for LLM consumption, and storing structured data in the cloud.

## 🎯 Overview

This project demonstrates a production-ready document processing pipeline that:
- Accepts PDF uploads via REST API
- Stores files in Google Drive (cloud storage)
- Extracts and processes text from PDFs
- Chunks text for LLM/RAG applications
- Creates Parquet files (columnar format for ML/AI)
- Tracks all metadata in PostgreSQL
- Provides REST API for all operations

## 🏗️ Architecture
```
┌─────────────────────────────────────────────────────────┐
│                    PDF PIPELINE                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  📤 Flask REST API (Port 5000)                          │
│     ├── POST /upload           Upload & process PDFs    │
│     ├── GET  /documents        List all documents       │
│     ├── GET  /documents/<id>   Get document details     │
│     └── GET  /documents/<id>/status  Check status       │
│                                                          │
│  ↓                                                       │
│                                                          │
│  🔧 Processing Pipeline                                  │
│     ├── Upload to Google Drive (upload/)                │
│     ├── Move through stages (staging → processing)      │
│     ├── Extract text (PyPDF2)                           │
│     ├── Clean & normalize text                          │
│     ├── Chunk for LLM (500 words, 50 overlap)           │
│     ├── Create Parquet file                             │
│     ├── Upload Parquet to Drive (parquet/)              │
│     └── Move PDF to processed (processed/)              │
│                                                          │
│  ↓                                                       │
│                                                          │
│  💾 Data Storage                                         │
│     ├── PostgreSQL: Metadata & tracking                 │
│     ├── Google Drive: PDF files (5 folders)             │
│     └── Google Drive: Parquet files                     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 📋 Tech Stack

- **Backend**: Python 3.11+
- **Web Framework**: Flask
- **Database**: PostgreSQL 15 (Docker)
- **ORM**: SQLAlchemy
- **Cloud Storage**: Google Drive API
- **PDF Processing**: PyPDF2
- **Data Format**: Parquet (Pandas, PyArrow)
- **Containerization**: Docker & Docker Compose

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker Desktop
- Google Cloud account (free tier)
- Git

### 1. Clone & Setup
```bash
git clone <your-repo>
cd pdf_pipeline_project

# Create virtual environment
python -m venv venv

# Activate (Windows Git Bash)
source venv/Scripts/activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start PostgreSQL (Docker)
```bash
# Start containers
docker-compose up -d

# Verify running
docker ps
```

### 3. Google Drive API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project: "PDF Pipeline"
3. Enable Google Drive API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json` → place in project root
6. First run will open browser for authentication

### 4. Initialize Database
```bash
python -m src.app.create_table
```

### 5. Start API Server
```bash
python -m src.app.flask_app
```

API available at: `http://localhost:5000`

## 📚 API Usage

### Upload a Document
```bash
curl -X POST -F "file=@document.pdf" http://localhost:5000/upload
```

Response:
```json
{
  "success": true,
  "message": "Document uploaded and processed successfully",
  "document": {
    "id": 1,
    "filename": "document.pdf",
    "status": "processed",
    "page_count": 10,
    "word_count": 5000,
    "chunk_count": 11,
    "current_folder": "processed"
  }
}
```

### List All Documents
```bash
curl http://localhost:5000/documents
```

### Get Document Details
```bash
curl http://localhost:5000/documents/1
```

### Check Processing Status
```bash
curl http://localhost:5000/documents/1/status
```

## 📁 Project Structure
```
pdf_pipeline_project/
├── docker-compose.yml          # PostgreSQL container config
├── credentials.json            # Google OAuth credentials
├── token.json                  # Saved auth token
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── src/app/
│   ├── __init__.py
│   ├── database.py             # Database connection & config
│   ├── models.py               # SQLAlchemy models
│   ├── gdrive_storage.py       # Google Drive storage manager
│   ├── pdf_processor.py        # PDF text extraction & processing
│   ├── parquet_creator.py      # Parquet file creation
│   ├── pipeline_integrated.py  # Full processing pipeline
│   └── flask_app.py            # REST API server
│
├── data/postgres/              # PostgreSQL data (persisted)
│
└── Google Drive Structure:
    ├── upload/                 # Initial upload location
    ├── staging/                # Staged for processing
    ├── processing/             # Currently processing
    ├── processed/              # Completed PDFs
    └── parquet/                # Chunked data files
```

## 🗄️ Database Schema

### documents table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| filename | String | Original filename |
| file_size | Integer | File size in bytes |
| status | String | Processing status |
| gdrive_upload_id | String | Google Drive file ID (upload) |
| gdrive_staging_id | String | Google Drive file ID (staging) |
| gdrive_processing_id | String | Google Drive file ID (processing) |
| gdrive_processed_id | String | Google Drive file ID (processed) |
| current_folder | String | Current location |
| page_count | Integer | Number of pages |
| word_count | Integer | Total words |
| chunk_count | Integer | Number of chunks created |
| created_at | Timestamp | Creation time |
| updated_at | Timestamp | Last update time |
| processed_at | Timestamp | Processing completion time |

## 🔧 Configuration

### Database Connection

Edit `src/app/database.py`:
```python
DATABASE_URL = "postgresql://pdfuser:securepass123@localhost:5432/pdf_pipeline"
```

### Chunk Settings

Edit `src/app/pdf_processor.py`:
```python
chunk_size = 500  # Words per chunk
overlap = 50      # Overlap between chunks
```

## 🧪 Testing

### Run Full Pipeline Test
```bash
python -m src.app.pipeline_integrated
```

### Test PDF Processing
```bash
python -m src.app.test_pdf_processing
```

### Test Storage Manager
```bash
python -m src.app.test_storage_manager
```

### Test CRUD Operations
```bash
python -m src.app.test_crud
```

## 📊 Monitoring

### Check PostgreSQL Data
```bash
docker exec -it pdf_pipeline_postgres psql -U pdfuser -d pdf_pipeline

# Inside PostgreSQL:
\dt                              # List tables
SELECT * FROM documents;         # View all documents
\q                              # Exit
```

### View Google Drive

Visit: https://drive.google.com

You'll see 5 folders with your processed files.

### View Parquet Files
```bash
python -m src.app.view_parquet
```

## 🛠️ Troubleshooting

### Port 5432 Already in Use
```bash
# Stop desktop PostgreSQL
net stop postgresql-x64-17

# Or use Services GUI (services.msc)
```

### Google Drive Authentication Failed

1. Delete `token.json`
2. Re-run any script
3. Complete OAuth flow in browser

### Docker Container Won't Start
```bash
# Stop all containers
docker-compose down

# Remove volumes
docker-compose down -v

# Restart fresh
docker-compose up -d
```

## 🎓 Learning Outcomes

This project demonstrates:
- ✅ RESTful API design (Flask)
- ✅ Database ORM patterns (SQLAlchemy)
- ✅ Cloud API integration (Google Drive)
- ✅ OAuth2 authentication
- ✅ Docker containerization
- ✅ File processing pipelines
- ✅ Structured data formats (Parquet)
- ✅ Production patterns (staging, error handling)

## 🚀 Production Deployment

### Environment Variables

Create `.env` file:
```env
DATABASE_URL=postgresql://user:pass@host:5432/db
GOOGLE_CREDENTIALS_PATH=/path/to/credentials.json
FLASK_ENV=production
```

### Docker Production
```bash
# Build production image
docker build -t pdf-pipeline .

# Run with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

## 📝 License

MIT License - See LICENSE file

## 👥 Author

Built as a learning project to understand production data pipelines.

## 🙏 Acknowledgments

- SQLAlchemy documentation
- Google Drive API documentation
- Flask documentation
- PyPDF2 library