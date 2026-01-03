# PDF Processing Pipeline - Portfolio Project

## Quick Links

- **Live Demo**: [Add if deployed]
- **GitHub**: [Your repo URL]
- **Documentation**: [README.md](README.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)

## Elevator Pitch

A production-ready document processing pipeline that accepts PDFs via REST API, extracts and processes text, chunks content for LLM consumption, stores structured data in Parquet format, and manages everything across cloud storage and PostgreSQL - all built from scratch in 16 hours.

## Key Highlights

- ✅ **Full-Stack**: Backend API + Database + Cloud Integration
- ✅ **Production-Ready**: Error handling, logging, documentation
- ✅ **Scalable Architecture**: Modular design, easy to extend
- ✅ **100% Test Success**: All components tested and verified
- ✅ **Cloud-Native**: Google Drive + Docker + PostgreSQL

## Tech Stack

**Backend**: Python, Flask, SQLAlchemy  
**Database**: PostgreSQL  
**Cloud**: Google Drive API, OAuth 2.0  
**Processing**: PyPDF2, Pandas, PyArrow  
**Infrastructure**: Docker, Docker Compose  

## What I Built

1. **REST API** with 5 endpoints for document management
2. **Processing Pipeline** that stages files through 5 folders
3. **Cloud Storage Manager** with OAuth 2.0 authentication
4. **PDF Processor** with text extraction and intelligent chunking
5. **Parquet Creator** for LLM-ready structured output
6. **Complete Documentation** including deployment guides

## Metrics

- **8 Sessions** over 4 weeks
- **~1,500 lines** of production code
- **10+ technologies** mastered
- **20+ files** created
- **100% test** success rate
- **8 documents** processed successfully

## Skills Demonstrated

- RESTful API Design
- Database Schema Design
- Cloud API Integration
- OAuth 2.0 Authentication
- File Processing Pipelines
- Docker Containerization
- Production Documentation
- Testing & QA
- Error Handling & Logging

## Sample Code

### API Endpoint
```python
@app.route('/upload', methods=['POST'])
def upload_document():
    file = request.files['file']
    doc = pipeline.process_document(file.path, file.filename)
    return jsonify({
        'success': True,
        'document': {
            'id': doc.id,
            'status': doc.status,
            'chunks': doc.chunk_count
        }
    })
```

### Storage Manager
```python
class GoogleDriveStorage:
    def move_file(self, file_id, source_folder, target_folder):
        source_id = self.get_or_create_folder(source_folder)
        target_id = self.get_or_create_folder(target_folder)
        self.service.files().update(
            fileId=file_id,
            addParents=target_id,
            removeParents=source_id
        ).execute()
```

## Architecture
```
Client → Flask API → Processing Pipeline → Google Drive
                    ↓
               PostgreSQL
```

## Real-World Applications

This architecture is used in:
- Document management systems
- RAG (Retrieval Augmented Generation) for LLMs
- Legal/medical document processing
- Knowledge base creation
- Data engineering pipelines

## What I Learned

- How to design and build production REST APIs
- Database ORM patterns with SQLAlchemy
- Cloud service integration (OAuth 2.0, Drive API)
- File processing and chunking strategies
- Docker containerization and orchestration
- Writing comprehensive technical documentation
- Testing and quality assurance practices

## Interview Talking Points

1. **System Design**: "I designed a multi-stage pipeline with clear separation of concerns..."
2. **Cloud Integration**: "I implemented OAuth 2.0 and integrated with Google Drive API..."
3. **Database**: "I used SQLAlchemy ORM with PostgreSQL for relational data..."
4. **Testing**: "I achieved 100% test success through comprehensive testing..."
5. **Documentation**: "I wrote production-grade documentation including deployment guides..."

## Future Enhancements

- [ ] Add background job processing (Celery)
- [ ] Implement caching layer (Redis)
- [ ] Add authentication (JWT)
- [ ] Support additional file formats
- [ ] Deploy to cloud (AWS/GCP/Azure)
- [ ] Add monitoring dashboard

## Contact

**Name**: RC  
**Email**: [Your Email]  
**LinkedIn**: [Your LinkedIn]  
**GitHub**: [Your GitHub]

---

*Built as part of a structured 4-week learning program covering backend development, cloud services, and DevOps.*