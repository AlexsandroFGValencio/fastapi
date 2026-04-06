"""
Worker process for background tasks.
This is a placeholder that can be extended with Celery, RQ, or other task queue systems.
"""
import asyncio
import logging
import signal
import sys

from trivaxion.infrastructure.config.settings import get_settings
from trivaxion.infrastructure.logging.logger import configure_logging

logger = logging.getLogger(__name__)


class Worker:
    def __init__(self) -> None:
        self.running = True
        self.settings = get_settings()
        
    def handle_shutdown(self, signum: int, frame: object) -> None:
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
        
    async def run(self) -> None:
        logger.info("Worker started")
        logger.info(f"Environment: {self.settings.environment}")
        logger.info(f"Redis URL: {self.settings.redis_url}")
        
        while self.running:
            await asyncio.sleep(1)
            
        logger.info("Worker stopped")


def main() -> None:
    configure_logging()
    
    worker = Worker()
    
    signal.signal(signal.SIGTERM, worker.handle_shutdown)
    signal.signal(signal.SIGINT, worker.handle_shutdown)
    
    try:
        asyncio.run(worker.run())
    except KeyboardInterrupt:
        logger.info("Worker interrupted by user")
    except Exception as e:
        logger.exception(f"Worker failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
