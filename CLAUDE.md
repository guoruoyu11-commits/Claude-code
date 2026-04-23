# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
npm run dev         # Start Vite dev server (localhost:5173)
npm run build       # Production build
npm run preview     # Preview production build

# Python scripts (use py, not python3, on this Windows machine)
py scripts/scrape_one.py <id>               # Scrape one machine's wiki page → public/data/machines/<id>.json
py scripts/scrape_one.py <id> --force       # Overwrite existing
py scripts/scrape_one.py <id> --debug       # Debug mode
py scripts/scrape_scheduler.py              # Batch-scrape all machines (skip existing)
py scripts/scrape_scheduler.py --delay 2.0  # Slow down to 2s/request
py scripts/scrape_scheduler.py --id <id>    # Scrape one machine via batch script
py scripts/translate_nodes.py <id>          # Translate one machine (node-based, recommended)
py scripts/translate_nodes.py <id> --force  # Overwrite existing translation
py scripts/translate_nodes.py <id> --model gemini-2.0-flash  # Use a different model
py scripts/translate_scheduler.py           # Batch-translate all machines
py scripts/translate_scheduler.py --id <id> # Translate one machine via batch script
py scripts/translate_scheduler.py --force   # Overwrite all existing translations
py scripts/translate_scheduler.py --delay 2.0  # Slow down inter-machine wait
```

Python dependencies: `pip install beautifulsoup4 playwright google-genai` then `py -m playwright install chromium`

Requires a `.env` file in the project root with `GEMINI_API_KEY=<your_key>`.

## Architecture

Vue 3 + Vite + vue-router app. Two routes:
- `/` → `HomePage.vue` — tier table with cost filter
- `/machine/:id` → `MachineDetailPage.vue` — machine detail with wiki content

**`src/data/machines.js`** — single source of truth for all machine data. Exports:
- `MACHINES` — array of `{ id, name, short, cost, tier, img, link? }`. `name` is Chinese. `img` is from `https://exvsdb.com/wp-content/images/exvs2ib/{id}.png`.
- `TIERS` — ordered array `['S','A+','A','A-','B+','B','B-','C']`
- `TIER_META` — maps tier string → `{ label, sub, cls }` where `cls` drives CSS class on tier label

**Component responsibilities:**
- `CostFilter.vue` — cost tab buttons using exvsdb.com images (`cost{N}.png` / `cost{N}_off.png`). Emits `update:modelValue`.
- `TierTable.vue` — groups filtered machines by tier, renders one `TierRow` per tier.
- `TierRow.vue` — tier label (colored by `.tier-label.{cls}`) + row of `MachineCard`s. Tier label colors defined here as scoped CSS `.tier-label.{cls}` — add new entries when adding tiers to `TIER_META`.
- `MachineCard.vue` — 127×55px card. Shows `machine.img` with cost badge overlay; falls back to gradient + `machine.short` if image missing. Clicking navigates to `/machine/:id`.

**Machine detail data flow:**
- `MachineDetailPage.vue` fetches `/data/machines/{id}_zh.json` first (Chinese), falls back to `/data/machines/{id}.json` (Japanese) if not available. Shows lang toggle only when Chinese version exists.
- `WikiContent.vue` renders content: prefers `content_nodes` (structured node tree) over `content_html` (raw HTML). All newly generated translations use `content_nodes`.
- JSON files live in `public/data/machines/` and are served as static assets.

**Data generation pipeline:**
1. `scripts/scrape_one.py` — fetches atwiki page for a machine (with Playwright fallback for JS-rendered pages), extracts HTML content, saves `public/data/machines/{id}.json` with `content_html` and `content_nodes`
2. `scripts/html_to_nodes.py` — converts `content_html` (raw Japanese HTML) into a compact `content_nodes` JSON tree; called automatically by `translate_nodes.py` when nodes are missing
3. `scripts/translate_nodes.py` — **standard translation script**: extracts only leaf Japanese text from nodes, pre-substitutes ~95 fixed terms via `ja_zh_dict.py` (zero API cost), sends remaining text in batches to Gemini as JSON arrays, saves `{id}_zh.json` with `content_nodes`. Supports checkpoint/resume via `{id}_zh_nodes_progress.json`.
4. `scripts/ja_zh_dict.py` — fixed Japanese→Chinese term dictionary (section headings, table column names, game terms). Provides `has_japanese()` and `apply_dict()`.
5. `generate_machines.py` (root) — parses saved HTML from exvsdb.com to regenerate `src/data/machines.js`
6. `translate_machines.py` (root) — replaces Japanese names with Chinese in `machines.js`

**Translation output format** (`{id}_zh.json`):
```json
{
  "status": "ok",
  "id": "m12504",
  "name": "...",
  "translated_at": "...",
  "model": "gemini-2.5-pro",
  "content_nodes": [...]
}
```
No `content_html` in translated output — only `content_nodes`.

**Failed translation tracking:** `public/data/translate_failed.json` stores IDs that failed last run; `translate_scheduler.py` retries these first on the next run.

`scripts/translate_one.py` (legacy HTML-based translation) is retained but no longer part of the standard pipeline.
