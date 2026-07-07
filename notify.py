import logging
import subprocess

logger = logging.getLogger(__name__)


def notify(body: str) -> None:
    """Send a macOS banner via osascript. Never raises."""
    try:
        safe_body = body.replace("\\", "\\\\").replace('"', '\\"')
        subprocess.run(
            [
                "osascript",
                "-e",
                f'display notification "{safe_body}" with title "ff_crawler" sound name "Glass"',
            ],
            check=False,
        )
    except Exception as exc:  # never let a notify failure kill the loop
        logger.warning("Failed to send notification: %s", exc)
