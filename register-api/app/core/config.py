from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "MDPs Artifact Catalog"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"  # Change this in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database Configuration
    DATABASE_URL: Optional[str] = "database_url"
    
    # Storage Configuration
    STORAGE_PATH: str = "./storage"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
    DESTINATION_REGISTRY : str = None

    # JWT Info
    JWT_AUTH_TYPE: str = "COGNITO" # one of: COGNITO, KEYCLOAK
    JWT_VALIDATION_URL: str = None
    JWT_ISSUER_URL: str = None
    JWT_CLIENT_ID: str = None
    JWT_GROUPS_KEY: str = None


    class Config:
        case_sensitive = True
        env_file = ".env"

# Create a global settings instance
settings = Settings() 