<template>
  <div>
    <!-- Machine count + Legend bar -->
    <div class="info-bar">
      <span class="machine-count">
        <b>{{ machines.length }}</b> 機体
      </span>
      <div class="legend">
        <span v-for="c in COSTS" :key="c" class="legend-item">
          <i class="legend-dot" :style="{ background: `var(--cost-${c})` }"></i>
          <span class="legend-label">{{ c }}</span>
        </span>
      </div>
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
.info-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 12px;
  padding: 0 2px;
}

.machine-count {
  font-size: 12px;
  color: var(--text-muted);
  letter-spacing: .3px;
}
.machine-count b {
  font-family: var(--font-ui);
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin-right: 2px;
}

.legend {
  display: flex;
  align-items: center;
  gap: 14px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 2px;
  display: inline-block;
  flex-shrink: 0;
  box-shadow: 0 0 6px currentColor;
}

.legend-label {
  font-family: var(--font-ui);
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  letter-spacing: .5px;
}

.tier-table {
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 4px 30px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.03);
}
</style>
