# Quick Start Guide

## 🚀 First Time Setup (5 min)
```bash
# 1. Run setup script
./setup.sh

# 2. Add Google credentials
# Download credentials.json from Google Cloud Console
# Place in project root

# 3. Start API
python -m src.app.flask_app
```

## 📤 Daily Usage

### Start Everything
```bash
# Activate venv
source venv/Scripts/activate  # Git Bash
# OR
venv\Scripts\activate         # CMD

# Start Docker (if not running)
docker-compose up -d

# Start API
python -m src.app.flask_app
```

### Upload a Document
```bash
curl -X POST -F "file=@document.pdf" http://localhost:5000/upload
```

### Check Documents
```bash
# List all
curl http://localhost:5000/documents

# Get specific
curl http://localhost:5000/documents/1

# Check status
curl http://localhost:5000/documents/1/status
```

### Stop Everything
```bash
# Stop Flask: Ctrl+C

# Stop Docker
docker-compose down
```

## 🔧 Common Commands

### Database
```bash
# Connect to PostgreSQL
docker exec -it pdf_pipeline_postgres psql -U pdfuser -d pdf_pipeline

# View documents
SELECT id, filename, status FROM documents;

# Exit
\q
```

### View Parquet Files
```bash
python -m src.app.view_parquet
```

### Run Tests
```bash
# Full pipeline
python -m src.app.pipeline_integrated

# CRUD operations
python -m src.app.test_crud

# Storage manager
python -m src.app.test_storage_manager
```

## 🐛 Troubleshooting

### Port 5432 in use
```bash
net stop postgresql-x64-17
```

### Reset database
```bash
docker-compose down -v
docker-compose up -d
python -m src.app.create_table
```

### Google auth issues
```bash
rm token.json
# Re-run any script to re-authenticate
```

## 📁 File Locations

- **Code**: `src/app/`
- **Credentials**: `credentials.json` (root)
- **Database**: `data/postgres/`
- **Logs**: `pipeline.log`
- **Google Drive**: https://drive.google.com