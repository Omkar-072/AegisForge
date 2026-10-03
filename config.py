import os
from dotenv import load_dotenv

# Load variables from a physical .env file if it exists
load_dotenv()

class Config:
    """Base configuration containing settings universal to all environments."""
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-super-secret-key-change-in-prod")
    DEBUG = False
    TESTING = False
    
    # Secure defaults for our engine limits
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Limit request bodies to 16MB

class DevelopmentConfig(Config):
    """Development environment specific overrides."""
    DEBUG = True
    ENV = "development"

class ProductionConfig(Config):
    """Production environment configurations ensuring strict guardrails."""
    ENV = "production"
    # Overriding default keys forces production environments to fail if secrets are leaked or missing
    SECRET_KEY = os.getenv("SECRET_KEY")

# Mapping dictionary to easily swap runtime contexts
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}