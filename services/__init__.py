"""
Services package for Web Browser Query Agent
Contains all core service modules
"""

# Import all services for easy access
from .query_classifier import QueryClassifier
from .similarity_search import SimilaritySearch
from .cache_manager import CacheManager
from .web_scraper import WebScraper
from .content_summarizer import ContentSummarizer

__all__ = [
    'QueryClassifier',
    'SimilaritySearch', 
    'CacheManager',
    'WebScraper',
    'ContentSummarizer'
]
