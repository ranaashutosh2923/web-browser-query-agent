"""
Web Scraper Service - FIXED VERSION
Uses Playwright to scrape Google/DuckDuckGo search results with improved reliability
"""

from playwright.sync_api import sync_playwright
import requests
from bs4 import BeautifulSoup
import logging
import time
from config import Config

logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self):
        """Initialize the web scraper"""
        self.max_pages = Config.MAX_SCRAPE_PAGES
        self.timeout = Config.SCRAPE_TIMEOUT * 1000  # Convert to milliseconds

    def search_google(self, query: str) -> list:
        """
        Search Google using Playwright - IMPROVED VERSION

        Args:
            query (str): Search query

        Returns:
            list: List of search result URLs
        """
        try:
            with sync_playwright() as p:
                # Launch browser with better settings
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage'
                    ]
                )
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                page = context.new_page()

                # Set longer timeout
                page.set_default_timeout(20000)

                # Search on Google
                search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                page.goto(search_url, wait_until='networkidle')

                # Wait a bit for dynamic content
                time.sleep(2)

                # Try multiple selectors for Google results
                results = []
                selectors_to_try = [
                    "div[id='search'] div.g a[href]",
                    "div#search a[href]",
                    "div.g a[href]", 
                    ".yuRUbf a[href]",
                    "h3 a[href]"
                ]

                for selector in selectors_to_try:
                    try:
                        links = page.query_selector_all(selector)
                        if links:
                            for link in links[:self.max_pages]:
                                href = link.get_attribute("href")
                                if href and href.startswith("http") and "google.com" not in href:
                                    results.append(href)
                            break
                    except Exception as e:
                        logger.debug(f"Selector {selector} failed: {e}")
                        continue

                browser.close()

                if results:
                    logger.info(f"Found {len(results)} Google search results for: {query}")
                else:
                    logger.warning(f"No Google results found for: {query}")

                return results[:self.max_pages]

        except Exception as e:
            logger.error(f"Error searching Google: {e}")
            return []

    def search_duckduckgo(self, query: str) -> list:
        """
        Search DuckDuckGo as fallback - IMPROVED VERSION

        Args:
            query (str): Search query

        Returns:
            list: List of search result URLs
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = context.new_page()

                # Set longer timeout
                page.set_default_timeout(20000)

                # Search on DuckDuckGo
                search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
                page.goto(search_url, wait_until='networkidle')

                # Wait for results to load
                time.sleep(3)

                # Try multiple selectors for DuckDuckGo results
                results = []
                selectors_to_try = [
                    "article[data-testid='result'] h2 a[href]",
                    "div[data-testid='result'] a[href]",
                    ".result a[href]",
                    "h2 a[href]"
                ]

                for selector in selectors_to_try:
                    try:
                        links = page.query_selector_all(selector)
                        if links:
                            for link in links[:self.max_pages]:
                                href = link.get_attribute("href")
                                if href and href.startswith("http") and "duckduckgo.com" not in href:
                                    results.append(href)
                            break
                    except Exception as e:
                        logger.debug(f"Selector {selector} failed: {e}")
                        continue

                browser.close()

                if results:
                    logger.info(f"Found {len(results)} DuckDuckGo search results for: {query}")
                else:
                    logger.warning(f"No DuckDuckGo results found for: {query}")

                return results[:self.max_pages]

        except Exception as e:
            logger.error(f"Error searching DuckDuckGo: {e}")
            return []

    def search_requests_fallback(self, query: str) -> list:
        """
        Fallback search using requests library

        Args:
            query (str): Search query

        Returns:
            list: List of search result URLs
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }

            # Try DuckDuckGo HTML search
            search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
            response = requests.get(search_url, headers=headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = []

                # Find result links
                for link in soup.find_all('a', class_='result-link'):
                    href = link.get('href')
                    if href and href.startswith('http'):
                        results.append(href)
                        if len(results) >= self.max_pages:
                            break

                logger.info(f"Found {len(results)} results using requests fallback for: {query}")
                return results

        except Exception as e:
            logger.error(f"Error in requests fallback: {e}")

        return []

    def scrape_webpage_content(self, url: str) -> dict:
        """
        Scrape content from a webpage

        Args:
            url (str): URL to scrape

        Returns:
            dict: Scraped content with title, text, and metadata
        """
        try:
            # Use requests with BeautifulSoup for faster scraping
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No title"

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Extract text content
            text_content = soup.get_text()

            # Clean up text
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            # Limit text length
            if len(text) > 5000:
                text = text[:5000] + "..."

            return {
                "url": url,
                "title": title_text,
                "content": text,
                "length": len(text),
                "scraped_at": time.time()
            }

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {
                "url": url,
                "title": "Error",
                "content": f"Failed to scrape content: {str(e)}",
                "length": 0,
                "scraped_at": time.time()
            }

    def search_and_scrape(self, query: str) -> dict:
        """
        Search and scrape top results for a query - IMPROVED WITH FALLBACKS

        Args:
            query (str): Search query

        Returns:
            dict: Search results with scraped content
        """
        logger.info(f"Starting search and scrape for: {query}")

        # Try multiple search methods
        search_urls = []

        # Try Google first
        search_urls = self.search_google(query)

        # If Google fails, try DuckDuckGo
        if not search_urls:
            logger.info("Google search failed, trying DuckDuckGo...")
            search_urls = self.search_duckduckgo(query)

        # If both fail, try requests fallback
        if not search_urls:
            logger.info("Playwright searches failed, trying requests fallback...")
            search_urls = self.search_requests_fallback(query)

        # If all searches fail, return sample URLs for demo
        if not search_urls:
            logger.warning("All search methods failed, using demo URLs...")
            search_urls = [
                f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}",
                f"https://www.britannica.com/search?query={query.replace(' ', '+')}"
            ]

        # Scrape content from each URL
        scraped_results = []
        for url in search_urls:
            content = self.scrape_webpage_content(url)
            scraped_results.append(content)
            time.sleep(1)  # Be respectful to servers

        search_engine = "google" if self.search_google(query) else ("duckduckgo" if self.search_duckduckgo(query) else "fallback")

        return {
            "query": query,
            "search_engine": search_engine,
            "results": scraped_results,
            "total_results": len(scraped_results),
            "scraped_at": time.time()
        }
