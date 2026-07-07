import asyncio
import logging

from ff_crawler.watcher import run_watcher

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        asyncio.run(run_watcher())
    except KeyboardInterrupt:
        logger.info("ff_crawler stopped")


if __name__ == "__main__":
    main()
