from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database connection URL
DATABASE_URL = "postgresql://pdfuser:securepass123@localhost:5432/pdf_pipeline"

# Create engine to connect to the database and enable echo for SQL logging
engine = create_engine(DATABASE_URL, echo=True)

# Create session maker for database sessions with autocommit and autoflush disabled by default
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models in SQLAlchemy ORM  
Base = declarative_base()

def get_db():
    """Dependency function to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()