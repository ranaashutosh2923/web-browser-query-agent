"""
Flask API Routes for Web Browser Query Agent
Provides REST API endpoints for the query agent
"""

from flask import Flask, request, jsonify, render_template
import logging
import sys
import os

# Add parent directory to path to import main modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import WebBrowserQueryAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')

    # Initialize the query agent
    try:
        agent = WebBrowserQueryAgent()
        logger.info("Query agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize query agent: {e}")
        agent = None

    @app.route('/')
    def index():
        """Serve the main web interface"""
        return render_template('index.html')

    @app.route('/api/query', methods=['POST'])
    def process_query():
        """Process a user query via API"""
        try:
            if not agent:
                return jsonify({
                    'error': 'Query agent not initialized',
                    'type': 'system_error'
                }), 500

            data = request.get_json()
            if not data or 'query' not in data:
                return jsonify({
                    'error': 'Query parameter is required',
                    'type': 'validation_error'
                }), 400

            query = data['query'].strip()
            if not query:
                return jsonify({
                    'error': 'Query cannot be empty',
                    'type': 'validation_error'
                }), 400

            # Process the query
            result = agent.process_query(query)

            return jsonify(result)

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return jsonify({
                'error': str(e),
                'type': 'processing_error'
            }), 500

    @app.route('/api/status')
    def system_status():
        """Get system status"""
        try:
            if not agent:
                return jsonify({
                    'status': 'error',
                    'message': 'Query agent not initialized'
                }), 500

            status = agent.get_system_status()
            return jsonify(status)

        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return jsonify({
                'error': str(e),
                'status': 'error'
            }), 500

    @app.route('/api/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'Web Browser Query Agent',
            'version': '1.0.0'
        })

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({
            'error': 'Endpoint not found',
            'type': 'not_found'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        return jsonify({
            'error': 'Internal server error',
            'type': 'server_error'
        }), 500

    return app

if __name__ == '__main__':
    """Run the Flask application"""
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
