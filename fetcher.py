import logging
import random

import httpx

logger = logging.getLogger(__name__)

_USER_AGENTS: tuple[str, ...] = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
)


def _build_headers() -> dict[str, str]:
    """Return request headers with a randomly chosen, realistic browser identity."""
    return {
        "User-Agent": random.choice(_USER_AGENTS),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "mk-MK,mk;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }


async def fetch(url: str, timeout: float) -> str | None:
    """GET url and return HTML text, or None on any failure (never raises)."""
    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers=_build_headers(),
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            html = response.text
    except httpx.HTTPStatusError as exc:
        logger.warning("HTTP %s while fetching %s", exc.response.status_code, url)
        return None
    except httpx.TimeoutException:
        logger.warning("Timeout while fetching %s", url)
        return None
    except httpx.HTTPError as exc:  # connection errors, SSL/TLS, too many redirects, etc.
        logger.warning("Network error while fetching %s: %s", url, exc)
        return None
    except Exception as exc:  # last-resort safety net
        logger.exception("Unexpected error while fetching %s: %s", url, exc)
        return None

    if not html or not html.strip():
        logger.warning("Empty response body from %s", url)
        return None
    return html
