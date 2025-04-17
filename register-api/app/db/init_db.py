from app.core.database import Base, engine
from app.models.job import Job
from app.models.application_package_db import ApplicationPackage
from app.core.config import settings



def init_db():

    from sqlalchemy import create_engine
    from sqlalchemy_utils import database_exists, create_database

    engine = create_engine(settings.DATABASE_URL)
    if not database_exists(engine.url):
        create_database(engine.url)

    print(database_exists(engine.url))




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