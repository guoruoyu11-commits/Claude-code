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
py scripts/translate_one.py <id>            # Translate one machine JSON to Chinese
py scripts/translate_scheduler.py           # Batch-translate all machines
```

Python dependencies: `pip install beautifulsoup4 playwright` then `py -m playwright install chromium`

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
- `MachineDetailPage.vue` fetches `/data/machines/{id}.json` (Japanese) and `/data/machines/{id}_zh.json` (Chinese) at runtime. Shows lang toggle only when Chinese version exists. Handles atwiki collapsible blocks (`.plugin-openclose`) via DOM manipulation after render.
- JSON files live in `public/data/machines/` and are served as static assets.

**Data generation pipeline:**
1. `scripts/scrape_one.py` — fetches atwiki page for a machine (with Playwright fallback for JS-rendered pages), extracts HTML content, saves `public/data/machines/{id}.json`
2. `scripts/translate_one.py` — translates the Japanese JSON to Chinese, saves `{id}_zh.json`
3. `generate_machines.py` (root) — parses saved HTML from exvsdb.com to regenerate `src/data/machines.js`
4. `translate_machines.py` (root) — replaces Japanese names with Chinese in `machines.js`
