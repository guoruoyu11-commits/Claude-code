<template>
  <div class="filter-wrap">
    <button
      v-for="cost in availableCosts"
      :key="cost"
      class="cost-tab"
      :class="{ active: modelValue === String(cost) }"
      @click="emit('update:modelValue', String(cost))"
    >
      <img
        :src="imgUrl(cost, modelValue === String(cost))"
        :alt="`${cost}コスト`"
        class="cost-img"
      />
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { MACHINES } from '../data/machines.js'

defineProps({
  modelValue: { type: String, default: '3000' },
})
const emit = defineEmits(['update:modelValue'])

const availableCosts = computed(() =>
  [...new Set(MACHINES.map(m => m.cost))].sort((a, b) => b - a)
)

const BASE = 'https://exvsdb.com/wp-content/images/exvs2ib/cost/'
function imgUrl(cost, active) {
  return active ? `${BASE}cost${cost}.png` : `${BASE}cost${cost}_off.png`
}
</script>

<style scoped>
.filter-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 12px;
}
.cost-tab {
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  opacity: 0.75;
  transition: opacity .15s, transform .15s;
}
.cost-tab:hover { opacity: 1; }
.cost-tab.active { opacity: 1; }

.cost-img {
  display: block;
  width: 240px;
  height: auto;
}
</style>
