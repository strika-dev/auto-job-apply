"""
Configuration management for Auto Job Apply
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Application configuration"""
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = "gpt-4"
    
    # Email
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL")
    
    # Database
    DATABASE_PATH = os.getenv("DATABASE_PATH", "data/applications.db")
    DATABASE_URL = f"sqlite:///{BASE_DIR / DATABASE_PATH}"
    
    # Resume
    BASE_RESUME_PATH = os.getenv("BASE_RESUME_PATH", "data/base_resume.txt")
    
    # Application
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    PORT = int(os.getenv("PORT", 5000))
    
    # Job Scraping
    SCRAPE_DELAY = 2  # Seconds between requests
    MAX_JOBS_PER_SEARCH = 50
    
    # Application Status Options
    STATUS_OPTIONS = [
        "pending",
        "applied",
        "interview_scheduled",
        "interviewed",
        "offer_received",
        "rejected",
        "withdrawn"
    ]


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


def get_config():
    """Get configuration based on environment"""
    env = os.getenv("FLASK_ENV", "development")
    if env == "production":
        return ProductionConfig()
    return DevelopmentConfig()
