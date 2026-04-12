<template>
  <div>
    <!-- Machine count -->
    <div class="machine-count">
      表示中機体数：<b>{{ machines.length }}</b> 機
    </div>

    <!-- Legend -->
    <div class="legend">
      <span class="legend-label">コスト色凡例：</span>
      <span v-for="c in COSTS" :key="c" class="legend-item">
        <i class="legend-dot" :style="{ background: `var(--cost-${c})` }"></i>{{ c }}
      </span>
    </div>

    <!-- Tier rows -->
    <div class="tier-table">
      <TierRow
        v-for="(tier, idx) in TIERS"
        :key="tier"
        :meta="TIER_META[tier]"
        :machines="byTier[tier] || []"
        :class="{ alt: idx % 2 === 1 }"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { TIERS, TIER_META } from '../data/machines.js'
import TierRow from './TierRow.vue'

const props = defineProps({
  machines: { type: Array, default: () => [] },
})

const COSTS = [3000, 2500, 2000, 1500]

const byTier = computed(() => {
  const map = {}
  for (const tier of TIERS) map[tier] = []
  for (const m of props.machines) {
    if (map[m.tier]) map[m.tier].push(m)
  }
  return map
})
</script>

<style scoped>
.machine-count {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 14px;
}
.machine-count b { color: var(--text-primary); font-weight: 700; }

.legend {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 6px;
  margin-bottom: 16px;
  font-size: 12px;
}
.legend-label { color: var(--text-muted); font-weight: 600; }
.legend-item  { display: flex; align-items: center; gap: 5px; }
.legend-dot   { width: 12px; height: 12px; border-radius: 3px; display: inline-block; flex-shrink: 0; }

.tier-table {
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}
</style>
