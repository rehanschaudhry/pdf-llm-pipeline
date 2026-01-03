from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from src.app.database import Base

class Document(Base):
    __tablename__ = "documents"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # File information
    filename = Column(String, nullable=False)
    file_size = Column(Integer)
    status = Column(String, default="uploaded")
    
    # Google Drive file IDs
    gdrive_upload_id = Column(String)
    gdrive_staging_id = Column(String)
    gdrive_processing_id = Column(String)
    gdrive_processed_id = Column(String)
    current_folder = Column(String)
    
    # Document metadata
    page_count = Column(Integer)
    word_count = Column(Integer)
    chunk_count = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename}, status={self.status})>"