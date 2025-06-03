import os
import time
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.exc import OperationalError
from alembic.config import Config
from alembic import command
from app.core.database import Base, engine
from app.core.config import settings
from fastapi.logger import logger

def wait_for_db(max_retries=5, retry_interval=5):
    """Wait for the database to become available."""
    retries = 0
    while retries < max_retries:
        try:
            SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
            engine = create_engine(SQLALCHEMY_DATABASE_URL)
            logger.info("Database is available!")
            return True
        except OperationalError:
            retries += 1
            if retries == max_retries:
                logger.error("Could not connect to database after maximum retries")
                return False
            logger.info(f"Database not available. Retrying in {retry_interval} seconds... (Attempt {retries}/{max_retries})")
            time.sleep(retry_interval)
    return False

def init_db():
    """Initialize the database with tables and run migrations."""
    try:
        # Wait for database to be available
        if not wait_for_db():
            raise Exception("Database connection failed")

        # # Create database if it doesn't exist
        # db_exists = database_exists(engine.url)
        # if not db_exists:
        #     print("Creating database")
        #     logger.info("Creating database...")
        #     create_database(engine.url)
        #     logger.info("Database created successfully!")

        # # Import all models to ensure they are registered with Base
        # from app.models import job
        # from app.models import application_package_db

        # Create all tables
        # logger.info("Creating database tables...")
        # Base.metadata.create_all(bind=engine)

        # Run Alembic migrations
        logger.info("Running database migrations...")
        alembic_cfg = Config("alembic.ini")
        # #if we created tables
        # if not db_exists:
        #     print("Creating checkpoint")
        #     # id the DB didn't exist, it will be created with the most
        #     # up to date schemas.
        #     command.stamp(alembic_cfg, "head")

        
        command.upgrade(alembic_cfg, "head")

        # Print out the created tables
        logger.info("\nCreated tables:")
        for table in Base.metadata.tables:
            logger.info(f"- {table}")

        logger.info("\nDatabase initialization completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    init_db() 