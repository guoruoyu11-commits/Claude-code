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

function imgUrl(cost, active) {
  return active ? `/images/cost/cost${cost}.png` : `/images/cost/cost${cost}_off.png`
}
</script>

<style scoped>
.filter-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 14px;
}
.cost-tab {
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  opacity: 0.75;
  border-radius: 6px;
  transition: opacity .15s, transform .15s, filter .15s;
}
.cost-tab:hover { opacity: 1; filter: brightness(1.05); }
.cost-tab.active { opacity: 1; transform: translateY(-1px); }

.cost-img {
  display: block;
  width: min(240px, calc((100vw - 72px) / 2));
  height: auto;
}

@media (max-width: 600px) {
  .filter-wrap {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .cost-img {
    width: 100%;
  }
}
</style>
