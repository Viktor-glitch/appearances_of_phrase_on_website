# ff_crawler

A tiny macOS watcher that periodically fetches the homepage of the Faculty of
Pharmacy (ff.ukim.edu.mk), counts how many times the Cyrillic phrase
„фармацевтска ботаника" appears in the page's visible text, and fires a native
macOS notification whenever that count rises above a configured baseline.

Deliberately minimal: no database, no web framework, no queue, no external
notification service. Just an asyncio loop, one HTTP GET per cycle, and
`osascript` banners.

## How it works

- Fetches `TARGET_URL` once per cycle (single GET, rotating browser headers).
- Strips the HTML to visible text and counts case-insensitive occurrences of
  `SEARCH_PHRASE`.
- A failed fetch never raises — it is logged and the cycle is skipped, so a
  network blip can't produce a false "count changed" alert.
- Two modes via `DRY_RUN`:
  - `DRY_RUN=true`: every cycle notifies the current count (use this once to
    read the number).
  - `DRY_RUN=false`: notifies only when the count rises above `BASELINE_COUNT`,
    and only once per new higher value (in-memory de-duplication).

## Run flow

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 1. set DRY_RUN=true, run, read the notified count:
python main.py
# 2. set BASELINE_COUNT=<that number> and DRY_RUN=false in .env, then:
python main.py
```

## Notes

- Works on macOS only (uses `osascript` for notifications).
- State is in-memory: a restart re-arms from `BASELINE_COUNT` (a restart while
  the count is already elevated may re-notify once — acceptable).
- The real `.env` is gitignored and never committed; commit only `.env.example`.
