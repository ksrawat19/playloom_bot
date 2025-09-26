import os
from threading import Thread
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def keep_alive(app):
    def run():
        port = int(os.getenv('PORT', 8080))
        logger.info(f"Starting Flask server on port {port}")
        app.run(host='0.0.0.0', port=port)
    logger.info("Starting keep_alive thread")
    t = Thread(target=run)
    t.start()
