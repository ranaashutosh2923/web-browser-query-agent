import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for Web Browser Query Agent"""

    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

    # Redis Configuration
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))

    # Vector Database
    CHROMA_PERSIST_DIRECTORY = os.getenv('CHROMA_PERSIST_DIRECTORY', './chroma_db')

    # Similarity Search
    SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', 0.8))

    # Web Scraping
    MAX_SCRAPE_PAGES = int(os.getenv('MAX_SCRAPE_PAGES', 5))
    SCRAPE_TIMEOUT = int(os.getenv('SCRAPE_TIMEOUT', 30))

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required")
        return True
