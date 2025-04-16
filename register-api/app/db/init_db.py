from app.core.database import Base, engine
from app.models.job import Job
from app.models.application_package_db import ApplicationPackage

def init_db():
    # Import all models here to ensure they are registered with Base
    from app.models import job
    from app.models import application_package_db
    
    print("Creating database tables...")
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Print out the created tables
    print("\nCreated tables:")
    for table in Base.metadata.tables:
        print(f"- {table}")
    
    print("\nDatabase tables created successfully!")

if __name__ == "__main__":
    init_db() 