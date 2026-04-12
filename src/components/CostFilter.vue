<template>
  <div class="filter-wrap">
    <!-- "全て" tab is always shown -->
    <button
      class="cost-tab"
      :class="{ active: modelValue === 'all' }"
      data-cost="all"
      @click="emit('update:modelValue', 'all')"
    >全て</button>

    <!-- Only render a tab when that cost actually exists in the data -->
    <button
      v-for="cost in availableCosts"
      :key="cost"
      class="cost-tab"
      :class="{ active: modelValue === String(cost) }"
      :data-cost="cost"
      @click="emit('update:modelValue', String(cost))"
    >{{ cost }}コスト</button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { MACHINES } from '../data/machines.js'

defineProps({
  modelValue: { type: String, default: 'all' },
})
const emit = defineEmits(['update:modelValue'])

// Derive unique sorted costs from the data instead of hard-coding
const availableCosts = computed(() =>
  [...new Set(MACHINES.map(m => m.cost))].sort((a, b) => b - a)
)
</script>

<style scoped>
.filter-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}
.cost-tab {
  padding: 7px 20px;
  border: 1.5px solid var(--border);
  border-radius: 20px;
  background: transparent;
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 600;
  transition: all .15s;
}
.cost-tab:hover { color: var(--text-primary); border-color: #555; }

/* Active states per cost */
.cost-tab[data-cost="all"].active  { background: var(--accent);       border-color: var(--accent);       color: #fff; }
.cost-tab[data-cost="3000"].active { background: var(--cost-3000);    border-color: var(--cost-3000);    color: #fff; }
.cost-tab[data-cost="2500"].active { background: var(--cost-2500);    border-color: var(--cost-2500);    color: #fff; }
.cost-tab[data-cost="2000"].active { background: var(--cost-2000);    border-color: var(--cost-2000);    color: #fff; }
.cost-tab[data-cost="1500"].active { background: var(--cost-1500);    border-color: var(--cost-1500);    color: #fff; }
</style>
