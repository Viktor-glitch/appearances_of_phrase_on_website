import asyncio
import logging

from .config import settings
from .counter import count_phrase
from .fetcher import fetch
from .notify import notify

logger = logging.getLogger(__name__)


async def run_watcher() -> None:
    last_notified = settings.baseline_count
    logger.info(
        "Starting ff_crawler (mode=%s, target=%s, phrase=%r, interval=%ss)",
        "dry-run" if settings.dry_run else "normal",
        settings.target_url,
        settings.search_phrase,
        settings.poll_interval_seconds,
    )
    while True:
        html = await fetch(settings.target_url, settings.request_timeout)
        if html is not None:
            count = count_phrase(html, settings.search_phrase)
            logger.info("Phrase %r appears %d time(s)", settings.search_phrase, count)
            if settings.dry_run:
                notify(
                    f"{settings.search_phrase} appears {count}× on ff.ukim.edu.mk"
                )
            elif count > settings.baseline_count and count > last_notified:
                notify(
                    f"'{settings.search_phrase}' increased: "
                    f"{settings.baseline_count} -> {count}"
                )
                last_notified = count
        await asyncio.sleep(settings.poll_interval_seconds)
