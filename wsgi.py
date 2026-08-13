"""
wsgi.py
-------
Production WSGI entry point for LifeXP using Waitress.
"""

import logging
from waitress import serve
from app import create_app

# Configure basic logging for the production server
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('waitress')

app = create_app()

if __name__ == "__main__":
    logger.info("Starting LifeXP production server on http://0.0.0.0:5000")
    serve(app, host='0.0.0.0', port=5000)
