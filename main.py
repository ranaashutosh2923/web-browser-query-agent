"""
Main Web Browser Query Agent
Orchestrates all components to process user queries
Updated to use services directory structure
"""

import logging
import time
import sys
import os
from datetime import datetime

# Add services directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

# Import all services from services directory
from config import Config
from services.query_classifier import QueryClassifier
from services.similarity_search import SimilaritySearch
from services.cache_manager import CacheManager
from services.web_scraper import WebScraper
from services.content_summarizer import ContentSummarizer

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebBrowserQueryAgent:
    def __init__(self):
        """Initialize the Web Browser Query Agent"""
        logger.info("Initializing Web Browser Query Agent...")

        # Validate configuration
        Config.validate_config()

        # Initialize all services
        self.classifier = QueryClassifier()
        self.similarity_search = SimilaritySearch()
        self.cache_manager = CacheManager()
        self.web_scraper = WebScraper()
        self.content_summarizer = ContentSummarizer()

        logger.info("Web Browser Query Agent initialized successfully!")

    def process_query(self, query: str) -> dict:
        """
        Process a user query through the complete pipeline

        Args:
            query (str): User query

        Returns:
            dict: Final response
        """
        start_time = time.time()
        logger.info(f"Processing query: {query}")

        try:
            # Step 1: Classify Query
            logger.info("Step 1: Classifying query...")
            classification = self.classifier.classify_query(query)

            if not classification['is_valid']:
                logger.info("Query classified as invalid")
                return {
                    "type": "invalid_query",
                    "query": query,
                    "response": self.classifier.get_invalid_response(query),
                    "reason": classification['reason'],
                    "processing_time": time.time() - start_time
                }

            logger.info("Query classified as valid")

            # Step 2: Check for similar queries
            logger.info("Step 2: Searching for similar queries...")
            similarity_result = self.similarity_search.search_similar_queries(query)

            if similarity_result['similar_found']:
                logger.info(f"Found {len(similarity_result['similar_queries'])} similar queries")

                # Step 3: Check cache for similar queries
                logger.info("Step 3: Checking cache for similar queries...")
                cached_result = self.cache_manager.get_similar_cached_results(
                    similarity_result['similar_queries']
                )

                if cached_result:
                    logger.info("Returning cached result for similar query")
                    cached_result['result']['cached'] = True
                    cached_result['result']['processing_time'] = time.time() - start_time
                    cached_result['result']['similar_query_used'] = True
                    return cached_result['result']

            # Step 4: No similar queries or cached results found - perform web search
            logger.info("Step 4: Performing web search and scraping...")
            search_results = self.web_scraper.search_and_scrape(query)

            if search_results['total_results'] == 0:
                return {
                    "type": "no_results",
                    "query": query,
                    "response": "Sorry, I couldn't find any relevant information for your query.",
                    "processing_time": time.time() - start_time
                }

            # Step 5: Summarize content
            logger.info("Step 5: Summarizing scraped content...")
            summary_result = self.content_summarizer.summarize_search_results(search_results)

            # Step 6: Create final response
            final_response = self.content_summarizer.create_cached_response(summary_result)
            final_response['processing_time'] = time.time() - start_time

            # Step 7: Cache the result
            logger.info("Step 6: Caching result...")
            self.cache_manager.cache_result(query, final_response)

            # Step 8: Add query to vector database for future similarity search
            logger.info("Step 7: Adding query to vector database...")
            self.similarity_search.add_query(query, {
                "timestamp": datetime.now().isoformat(),
                "result_type": final_response['type']
            })

            logger.info(f"Query processed successfully in {final_response['processing_time']:.2f} seconds")
            return final_response

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "type": "error",
                "query": query,
                "response": f"An error occurred while processing your query: {str(e)}",
                "processing_time": time.time() - start_time
            }

    def get_system_status(self) -> dict:
        """Get system status and statistics"""
        try:
            cache_stats = self.cache_manager.get_cache_stats()

            return {
                "status": "online",
                "components": {
                    "classifier": "online",
                    "similarity_search": "online", 
                    "cache_manager": "online" if self.cache_manager.redis_client else "offline",
                    "web_scraper": "online",
                    "content_summarizer": "online"
                },
                "cache_stats": cache_stats,
                "config": {
                    "similarity_threshold": Config.SIMILARITY_THRESHOLD,
                    "max_scrape_pages": Config.MAX_SCRAPE_PAGES
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

# Example usage and Flask app runner
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Web Browser Query Agent")
    parser.add_argument('--mode', choices=['test', 'api'], default='test',
                        help='Run mode: test queries or start API server')
    parser.add_argument('--host', default='0.0.0.0', help='API server host')
    parser.add_argument('--port', type=int, default=5000, help='API server port')

    args = parser.parse_args()

    if args.mode == 'test':
        # Test mode - run example queries
        agent = WebBrowserQueryAgent()

        test_queries = [
            "Best places to visit in Delhi",
            "walk my pet, add apples to grocery",  # Invalid query
            "How to learn Python programming",
            "Top tourist attractions in Delhi"  # Similar to first query
        ]

        for query in test_queries:
            print(f"\n{'='*50}")
            print(f"Query: {query}")
            print(f"{'='*50}")

            result = agent.process_query(query)

            print(f"Type: {result['type']}")
            print(f"Response: {result.get('response', result.get('answer', 'No response'))}")
            print(f"Processing time: {result['processing_time']:.2f} seconds")

            if 'sources' in result:
                print(f"Sources: {result['total_sources']}")

            print()

    elif args.mode == 'api':
        # API mode - start Flask server
        from api.routes import create_app

        app = create_app()
        print(f"\n🚀 Starting Web Browser Query Agent API server...")
        print(f"📡 Server running at: http://{args.host}:{args.port}")
        print(f"🌐 Web interface: http://{args.host}:{args.port}")
        print(f"📊 API status: http://{args.host}:{args.port}/api/status")
        print(f"\nPress Ctrl+C to stop the server\n")

        app.run(debug=True, host=args.host, port=args.port)
