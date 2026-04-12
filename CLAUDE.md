# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
py <script>.py      # Run Python scripts (use py, not python3, on this Windows machine)
npm run dev         # Start Vite dev server (already running on localhost:5173)
npm run build       # Production build
npm run preview     # Preview production build
```

## Architecture

Vue 3 + Vite single-page app. No router — one page only.

**Data flow:** `App.vue` holds `selectedCost` (ref, default `'3000'`), filters `MACHINES` into `filteredMachines`, passes to `TierTable`.

**`src/data/machines.js`** — single source of truth. Exports:
- `MACHINES` — array of `{ id, name, short, cost, tier, img }`. `name` is Chinese. `img` is the full URL from `https://exvsdb.com/wp-content/images/exvs2ib/{id}.png`.
- `TIERS` — ordered array `['S','A+','A','A-','B+','B','B-','C']`
- `TIER_META` — maps tier string → `{ label, sub, cls }` where `cls` drives CSS class on tier label

**Component responsibilities:**
- `CostFilter.vue` — renders cost tab buttons using exvsdb.com images (`cost{N}.png` active, `cost{N}_off.png` inactive). Emits `update:modelValue`.
- `TierTable.vue` — groups filtered machines by tier using `TIERS` order, renders one `TierRow` per tier.
- `TierRow.vue` — shows tier label (colored by `.tier-label.{cls}`) + row of `MachineCard`s.
- `MachineCard.vue` — 127×55px card. Shows `machine.img` (object-fit: cover) with cost badge overlay; falls back to cost-colored gradient + `machine.short` text if image missing/broken.

**Tier label colors** are defined in `TierRow.vue` scoped CSS as `.tier-label.{cls}` — must add new entries here when adding new tiers to `TIER_META`.

**Machine data generation:** `generate_machines.py` parses `view-source_https___exvsdb.com_exvs2ib_rank_.html` (saved page source) to extract machine id, name, cost, tier, and image URL, then writes `src/data/machines.js`. `translate_machines.py` replaces Japanese names with Chinese in `machines.js`.
