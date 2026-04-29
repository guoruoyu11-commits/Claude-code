<template>
  <div class="tier-table">
    <TierRow
      v-for="(tier, idx) in TIERS"
      :key="tier"
      :meta="TIER_META[tier]"
      :machines="byTier[tier] || []"
      :class="{ alt: idx % 2 === 1 }"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { TIERS, TIER_META } from '../data/machines.js'
import TierRow from './TierRow.vue'

const props = defineProps({
  machines: { type: Array, default: () => [] },
})

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
.tier-table {
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 4px 30px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.03);
}
</style>
