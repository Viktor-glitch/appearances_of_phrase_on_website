# ff_crawler — Plan

A tiny standalone watcher that periodically fetches
`http://www.ff.ukim.edu.mk/`, counts how many times the phrase
**„фармацевтска ботаника"** appears in the page's visible text, and fires a
**macOS notification** whenever that count rises above a configured baseline.

This is a separate project from `fastapi-project`. It **reuses the fetch
strategy** (async `httpx` + rotating realistic browser headers) from
`fastapi-project/app/services/scraper_engine.py`, but not the article-extraction
pipeline — we only need raw HTML and a text-strip + count.

## Decisions (locked)

| Question        | Choice                                            |
|-----------------|---------------------------------------------------|
| Notification    | macOS native banner (`osascript`), no external deps |
| Crawl scope     | Single homepage only (one GET, count in that page)  |
| Scheduler       | Standalone Python `asyncio` loop, `sleep(60)`       |
| Matching        | Visible text (HTML stripped), case-insensitive      |

## What gets reused vs. new

**Reused (copied/adapted, not imported — separate project):**
- `_USER_AGENTS` pool + `_build_headers()` — rotating browser identity so the
  UKIM host doesn't drop us.
- The defensive `httpx.AsyncClient` GET block: `follow_redirects=True`, timeout,
  and the layered `HTTPStatusError` / `TimeoutException` / `HTTPError` /
  catch-all handling that **never raises** — a failed fetch just logs and is
  skipped that cycle (no false "count changed" alerts).

**New:**
- Visible-text extraction: `BeautifulSoup(html).get_text(" ")` (drop
  `<script>`/`<style>` first), lowercase, then `str.count()` of the lowercased
  phrase. Also strip NUL/normalize whitespace so counting is stable.
- Baseline + dry-run logic.
- macOS notification helper.
- The every-minute loop.

## Config (`.env`, read via pydantic-settings)

```
TARGET_URL=http://www.ff.ukim.edu.mk/
SEARCH_PHRASE=фармацевтска ботаника
BASELINE_COUNT=0
POLL_INTERVAL_SECONDS=60
DRY_RUN=false
REQUEST_TIMEOUT=20
```

`.env.example` committed; real `.env` gitignored (never read/committed).

### Dry-run → baseline workflow (the flow you described)

- **`DRY_RUN=true`**: every cycle sends a notification reporting the **current
  count** (e.g. "фармацевтска ботаника appears 3× on ff.ukim.edu.mk"),
  regardless of baseline. You run it once, read the number, then set
  `BASELINE_COUNT=<that number>` in `.env` and flip `DRY_RUN=false`.
- **`DRY_RUN=false`** (normal): notify **only when `count > BASELINE_COUNT`**.
  The notification names the old vs new count. To avoid spamming one banner per
  minute once it's up, we notify on **each increase from the last seen value**
  (in-memory `last_notified_count`), not every cycle while it stays elevated.

## File layout

```
ff_crawler/
├── PLAN.md                 # this file
├── README.md               # how to run
├── requirements.txt        # httpx, beautifulsoup4, brotli, pydantic-settings
├── .env.example
├── .gitignore              # .env, __pycache__
└── ff_crawler/
    ├── __init__.py
    ├── config.py           # Settings(BaseSettings) — mirrors fastapi-project style
    ├── fetcher.py          # reused headers + defensive httpx GET -> html | None
    ├── counter.py          # html -> visible-text -> case-insensitive phrase count
    ├── notify.py           # macOS osascript banner
    └── watcher.py          # asyncio loop: fetch -> count -> compare -> notify
└── main.py                 # entrypoint: `python main.py`
```

## Core logic (`watcher.py`)

```
load settings
last_notified = BASELINE_COUNT
loop forever:
    html = await fetch(TARGET_URL)          # None on failure -> log + skip
    if html is not None:
        count = count_phrase(html, SEARCH_PHRASE)
        log(count)
        if DRY_RUN:
            notify(f"current count = {count}")
        elif count > BASELINE_COUNT and count > last_notified:
            notify(f"increased: {BASELINE_COUNT} -> {count}")
            last_notified = count
    await asyncio.sleep(POLL_INTERVAL_SECONDS)
```

## Notification (`notify.py`)

```python
subprocess.run([
    "osascript", "-e",
    f'display notification "{body}" with title "ff_crawler" sound name "Glass"'
])
```
(Escape quotes in `body`; wrap in try/except so a notify failure never kills the loop.)

## Matching detail

`count_phrase(html, phrase)`:
1. `soup = BeautifulSoup(html, "html.parser")`; remove `script`/`style` tags.
2. `text = soup.get_text(" ")`, collapse whitespace, strip NUL.
3. `return text.lower().count(phrase.lower().strip())`.

Case-insensitive via `.lower()`. Cyrillic lowercasing is handled by Python's
Unicode-aware `str.lower()`. Non-overlapping `str.count` is fine here.

## Run

```
cd ff_crawler
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env         # first: set DRY_RUN=true, run, read count
python main.py               # then set BASELINE_COUNT, DRY_RUN=false, rerun
```

## Open notes / non-goals

- No DB, no FastAPI, no queue — deliberately minimal.
- State (`last_notified`) is in-memory; restart re-arms from `BASELINE_COUNT`.
  A restart while the count is already elevated will re-notify once — acceptable.
- Single-page only; if the phrase later needs to be tracked across sub-pages,
  the fetcher is structured so a link-following arm can be added without
  touching the counter/notify layers.
```
