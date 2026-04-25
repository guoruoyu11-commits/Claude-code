# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
npm run dev         # Start Vite dev server (localhost:5173)
npm run build       # Production build
npm run preview     # Preview production build

# Python scripts (use py, not python3, on this Windows machine)
py scripts/pipeline.py <id> [<id2> ...]          # Full pipeline: scrape → translate → localize images
py scripts/pipeline.py <id> --force              # Force re-scrape and re-translate
py scripts/pipeline.py <id> --skip-scrape        # Skip scraping, translate only
py scripts/pipeline.py <id> --model gemini-2.0-flash  # Use a specific model
py scripts/pipeline.py <id> --workers 10         # Parallel workers (batch mode)
py scripts/pipeline.py <id> --retries 2          # Retry failed machines N times

py scripts/scrape_one.py <id>                    # Scrape one machine's wiki page → public/data/machines/<id>.json
py scripts/scrape_one.py <id> --force            # Overwrite existing
py scripts/scrape_scheduler.py                   # Batch-scrape all machines (skip existing)

py scripts/translate_nodes.py <id>               # Translate one machine
py scripts/translate_nodes.py <id> --force       # Overwrite existing translation
py scripts/translate_scheduler.py                # Batch-translate all machines
py scripts/translate_scheduler.py --force        # Overwrite all existing translations

py scripts/download_assets.py                    # Download machine + cost images → public/images/
py scripts/localize_wiki_images.py               # Replace atwiki image URLs in JSON with local /images/machines/{num}.png
```

Python dependencies: `pip install beautifulsoup4 playwright google-genai` then `py -m playwright install chromium`

Requires a `.env` file in the project root with `GEMINI_API_KEY=<your_key>`.

## Architecture

Vue 3 + Vite + vue-router app. Two routes:
- `/` → `HomePage.vue` — tier table with cost filter
- `/machine/:id` → `MachineDetailPage.vue` — machine detail with wiki content

**`src/data/machines.js`** — single source of truth for all machine data. Exports:
- `MACHINES` — array of `{ id, name, short, cost, tier, img }`. `name` is Chinese.
- `TIERS` — ordered array `['S','A+','A','A-','B+','B','B-','C']`
- `TIER_META` — maps tier string → `{ label, sub, cls }` where `cls` drives CSS class on tier label

**Component responsibilities:**
- `CostFilter.vue` — cost tab buttons using local `/images/cost/cost{N}.png` images. Emits `update:modelValue`.
- `TierTable.vue` — groups filtered machines by tier, renders one `TierRow` per tier.
- `TierRow.vue` — tier label + row of `MachineCard`s.
- `MachineCard.vue` — 127×55px card with cost badge; falls back to gradient + `machine.short` if image missing.
- `WikiContent.vue` — renders `content_nodes` tree. Handles: collapse sections, sub-page link routing, external link filtering (whitelist: `web.vsmobile.jp` only), and hides "参考資料/外部リンク/参戦PV" sections automatically.

**Machine detail data flow:**
- `MachineDetailPage.vue` fetches `/data/machines/{id}_zh.json` (Chinese), falls back to `{id}.json` (Japanese).
- JSON files in `public/data/machines/` are static assets served directly.
- Sub-pages stored as `{id}_p{pageNum}.json` and `{id}_p{pageNum}_zh.json`.

**Data generation pipeline:**
1. `scripts/pipeline.py` — **main entry point**: orchestrates scrape → translate → localize for one or more machines. Supports parallel workers (`--workers`), retry (`--retries`), and skip flags.
2. `scripts/scrape_one.py` — fetches atwiki page (Playwright fallback for JS-rendered pages), saves `{id}.json` with `content_html` and `content_nodes`. Detects and scrapes sub-pages automatically.
3. `scripts/html_to_nodes.py` — converts `content_html` into `content_nodes` JSON tree; called by `translate_nodes.py` when nodes are missing.
4. `scripts/translate_nodes.py` — extracts leaf Japanese text from nodes, pre-substitutes ~95 fixed terms via `ja_zh_dict.py`, sends batches to Gemini as `[{"id": N, "t": "text"}]` arrays (ID-based to handle partial responses), saves `{id}_zh.json`. Supports checkpoint/resume via `{id}_zh_nodes_progress.json`. Handles sub-pages automatically.
5. `scripts/ja_zh_dict.py` — fixed Japanese→Chinese term dictionary.
6. `scripts/localize_wiki_images.py` — replaces atwiki image URLs in JSON files with local paths.
7. `generate_machines.py` (root) — regenerates `src/data/machines.js` from exvsdb.com HTML.
8. `translate_machines.py` (root) — replaces Japanese names with Chinese in `machines.js`.

**Translation output format** (`{id}_zh.json`):
```json
{
  "status": "ok",
  "id": "m12504",
  "name": "...",
  "translated_at": "...",
  "model": "gemini-2.5-flash",
  "content_nodes": [...],
  "translation_log": [
    { "source": "原文", "target": "译文", "method": "dict", "node_type": "td" },
    { "source": "原文", "target": "译文", "method": "gemini", "node_type": "p" }
  ]
}
```

**Failed translation tracking:** `public/data/translate_failed.json` stores IDs that failed; `translate_scheduler.py` retries these first on the next run.

## Deployment

Production: Docker container on Alibaba Cloud ECS, nginx on ports 80 (HTTP→HTTPS redirect) and 443 (HTTPS).

**CI/CD** (`.github/workflows/deploy.yml`): push to `main` → build on GitHub runner → push Docker image to GHCR → SSH to ECS → pull and restart container.

**Required GitHub Secrets:**

| Secret | Description |
|--------|-------------|
| `GH_PAT` | GitHub PAT with `read:packages` scope |
| `ECS_HOST` | ECS public IP |
| `ECS_USERNAME` | SSH username |
| `ECS_SSH_KEY` | SSH private key content |

**SSL:** Certificates mounted from ECS host at `/etc/ssl/exvsdb/` (`.pem` and `.key`). Must be placed on the ECS machine manually; nginx reads them via Docker volume mount.

**Local Docker build:**
```bash
docker build -t exvsdb .
docker run -p 80:80 -p 443:443 exvsdb
```
