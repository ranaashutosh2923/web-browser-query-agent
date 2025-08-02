"""
Content Summarizer Service - FIXED VERSION
Summarizes scraped web content using Gemini LLM
"""

import google.generativeai as genai
from config import Config
import logging
import time

logger = logging.getLogger(__name__)

class ContentSummarizer:
    def __init__(self):
        """Initialize the Content Summarizer with Gemini API"""
        genai.configure(api_key=Config.GEMINI_API_KEY)
        # Fixed: Use correct model name
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def summarize_single_content(self, content: dict, query: str) -> str:
        """
        Summarize content from a single webpage

        Args:
            content (dict): Scraped content from webpage
            query (str): Original user query for context

        Returns:
            str: Summarized content
        """
        try:
            title = content.get('title', 'No title')
            text = content.get('content', '')
            url = content.get('url', '')

            if not text or len(text.strip()) < 50:
                return f"Insufficient content from {url}"

            prompt = f"""
            Summarize the following webpage content in relation to the user query.
            Be concise but informative, focusing on information relevant to the query.

            User Query: "{query}"

            Webpage Title: {title}
            URL: {url}

            Content:
            {text[:3000]}  # Limit content length for API

            Provide a clear, informative summary in 2-3 paragraphs:
            """

            response = self.model.generate_content(prompt)
            summary = response.text.strip()

            logger.info(f"Content summarized for {url}")
            return summary

        except Exception as e:
            logger.error(f"Error summarizing content: {e}")
            return f"Error summarizing content from {content.get('url', 'unknown')}: {str(e)}"

    def summarize_search_results(self, search_results: dict) -> dict:
        """
        Summarize all search results and create final response

        Args:
            search_results (dict): Complete search results with scraped content

        Returns:
            dict: Final summarized response
        """
        try:
            query = search_results.get('query', '')
            results = search_results.get('results', [])

            if not results:
                return {
                    "query": query,
                    "summary": "No search results found for your query.",
                    "sources": [],
                    "total_sources": 0
                }

            # Summarize each result
            summaries = []
            sources = []

            for i, result in enumerate(results[:5]):  # Limit to top 5
                summary = self.summarize_single_content(result, query)
                summaries.append({
                    "source_number": i + 1,
                    "title": result.get('title', 'No title'),
                    "url": result.get('url', ''),
                    "summary": summary
                })
                sources.append({
                    "title": result.get('title', 'No title'),
                    "url": result.get('url', '')
                })

            # Create overall summary
            combined_content = "\n\n".join([s['summary'] for s in summaries])

            overall_prompt = f"""
            Based on the following search results and summaries, create a comprehensive answer to the user's query.
            Combine information from multiple sources and provide a well-structured response.

            User Query: "{query}"

            Search Result Summaries:
            {combined_content}

            Provide a comprehensive answer that:
            1. Directly addresses the user's query
            2. Combines information from the sources
            3. Is well-structured and easy to read
            4. Mentions key sources when relevant

            Final Answer:
            """

            response = self.model.generate_content(overall_prompt)
            final_summary = response.text.strip()

            return {
                "query": query,
                "summary": final_summary,
                "detailed_summaries": summaries,
                "sources": sources,
                "total_sources": len(sources),
                "search_engine": search_results.get('search_engine', 'unknown')
            }

        except Exception as e:
            logger.error(f"Error creating final summary: {e}")
            return {
                "query": query,
                "summary": f"Error creating summary: {str(e)}",
                "sources": [],
                "total_sources": 0
            }

    def create_cached_response(self, summary_result: dict) -> dict:
        """
        Create response suitable for caching

        Args:
            summary_result (dict): Summarized results

        Returns:
            dict: Response ready for caching and user delivery
        """
        return {
            "type": "search_result",
            "query": summary_result.get('query', ''),
            "answer": summary_result.get('summary', ''),
            "sources": summary_result.get('sources', []),
            "total_sources": summary_result.get('total_sources', 0),
            "search_engine": summary_result.get('search_engine', 'unknown'),
            "cached": False,  # This will be set to True when retrieved from cache
            "timestamp": time.time()
        }
