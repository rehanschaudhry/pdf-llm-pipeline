from src.app.database import Base, engine
from src.app.models import Document

# Create all tables in the database based on the defined models 
Base.metadata.create_all(bind=engine)

print("✓ Tables created successfully!")