"""
Query Classifier Service - FIXED VERSION
Classifies user queries as valid or invalid using Gemini LLM
"""

import google.generativeai as genai
from config import Config
import logging

logger = logging.getLogger(__name__)

class QueryClassifier:
    def __init__(self):
        """Initialize the Query Classifier with Gemini API"""
        genai.configure(api_key=Config.GEMINI_API_KEY)
        # Fixed: Use correct model name
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def classify_query(self, query: str) -> dict:
        """
        Classify a query as valid or invalid

        Args:
            query (str): The user query to classify

        Returns:
            dict: {
                "is_valid": bool,
                "reason": str,
                "classification": str
            }
        """
        try:
            prompt = f"""
            Classify the following query as VALID or INVALID for web search.

            VALID queries are:
            - Questions that can be answered by searching the web
            - Requests for information, facts, or data
            - How-to questions
            - Location-based queries
            - Product or service inquiries

            INVALID queries are:
            - Personal tasks or commands (like "walk my pet", "add to grocery list")
            - Queries with multiple unrelated requests
            - Nonsensical or gibberish text
            - Personal actions that cannot be searched online

            Query: "{query}"

            Respond in exactly this format:
            CLASSIFICATION: [VALID/INVALID]
            REASON: [Brief explanation]
            """

            response = self.model.generate_content(prompt)
            result_text = response.text.strip()

            # Parse the response
            lines = result_text.split('\n')
            classification = None
            reason = None

            for line in lines:
                if line.startswith('CLASSIFICATION:'):
                    classification = line.split(':', 1)[1].strip()
                elif line.startswith('REASON:'):
                    reason = line.split(':', 1)[1].strip()

            is_valid = classification == 'VALID'

            logger.info(f"Query classified: {query} -> {classification}")

            return {
                "is_valid": is_valid,
                "reason": reason or "No reason provided",
                "classification": classification or "UNKNOWN"
            }

        except Exception as e:
            logger.error(f"Error classifying query: {e}")
            # Default to valid if there's an error
            return {
                "is_valid": True,
                "reason": f"Classification error: {str(e)}",
                "classification": "ERROR"
            }

    def get_invalid_response(self, query: str) -> str:
        """Get response for invalid queries"""
        return "This is not a valid query."
