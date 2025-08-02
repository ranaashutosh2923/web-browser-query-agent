"""
Similarity Search Service - FIXED VERSION
Uses ChromaDB and embeddings to find similar past queries
"""

import chromadb
from chromadb.config import Settings
import google.generativeai as genai
from config import Config
import logging
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)

class SimilaritySearch:
    def __init__(self):
        """Initialize ChromaDB and embedding model"""
        genai.configure(api_key=Config.GEMINI_API_KEY)

        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=Config.CHROMA_PERSIST_DIRECTORY,
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="query_embeddings",
            metadata={"description": "Web query embeddings for similarity search"}
        )

        logger.info("ChromaDB initialized successfully")

    def get_embedding(self, text: str) -> list:
        """Get embedding for text using Gemini - FIXED VERSION"""
        try:
            # Fixed: Use correct embedding model
            result = genai.embed_content(
                model='models/text-embedding-004',
                content=text,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return []

    def search_similar_queries(self, query: str, threshold: float = None) -> dict:
        """
        Search for similar queries in the vector database

        Args:
            query (str): The query to search for
            threshold (float): Similarity threshold (default from config)

        Returns:
            dict: {
                "similar_found": bool,
                "similar_queries": list,
                "similarities": list,
                "best_match": dict or None
            }
        """
        try:
            if threshold is None:
                threshold = Config.SIMILARITY_THRESHOLD

            # Get embedding for the query
            query_embedding = self.get_embedding(query)
            if not query_embedding:
                return {"similar_found": False, "similar_queries": [], "similarities": [], "best_match": None}

            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=5  # Get top 5 similar queries
            )

            if not results['ids'][0]:  # No results found
                return {"similar_found": False, "similar_queries": [], "similarities": [], "best_match": None}

            # Filter results by threshold
            similar_queries = []
            similarities = []
            documents = results['documents'][0]
            distances = results['distances'][0]
            metadatas = results['metadatas'][0]

            for i, distance in enumerate(distances):
                similarity = 1 - distance  # Convert distance to similarity
                if similarity >= threshold:
                    similar_queries.append({
                        "query": documents[i],
                        "similarity": similarity,
                        "metadata": metadatas[i]
                    })
                    similarities.append(similarity)

            # Sort by similarity (highest first)
            similar_queries.sort(key=lambda x: x['similarity'], reverse=True)

            best_match = similar_queries[0] if similar_queries else None

            logger.info(f"Found {len(similar_queries)} similar queries for: {query}")

            return {
                "similar_found": len(similar_queries) > 0,
                "similar_queries": similar_queries,
                "similarities": similarities,
                "best_match": best_match
            }

        except Exception as e:
            logger.error(f"Error searching similar queries: {e}")
            return {"similar_found": False, "similar_queries": [], "similarities": [], "best_match": None}

    def add_query(self, query: str, metadata: dict = None) -> bool:
        """
        Add a new query to the vector database

        Args:
            query (str): The query to add
            metadata (dict): Additional metadata

        Returns:
            bool: Success status
        """
        try:
            # Generate unique ID for the query
            query_id = hashlib.md5(query.encode()).hexdigest()

            # Get embedding
            embedding = self.get_embedding(query)
            if not embedding:
                return False

            # Prepare metadata
            if metadata is None:
                metadata = {}
            metadata.update({
                "query_text": query,
                "added_timestamp": str(datetime.now())
            })

            # Add to ChromaDB
            self.collection.add(
                embeddings=[embedding],
                documents=[query],
                metadatas=[metadata],
                ids=[query_id]
            )

            logger.info(f"Query added to vector database: {query}")
            return True

        except Exception as e:
            logger.error(f"Error adding query: {e}")
            return False
