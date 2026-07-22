"""
Application Entry Point
Run this file to start the Flask development server
"""
import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env file
load_dotenv()

# Create Flask app
app = create_app()

if __name__ == '__main__':
    # Get configuration from environment
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Run development server
    app.run(host=host, port=port, debug=debug)
