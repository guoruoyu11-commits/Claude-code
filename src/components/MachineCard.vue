<template>
  <div class="machine-card">
    <!-- Real image; falls back to gradient when src is empty or broken -->
    <div class="machine-thumb" :class="`thumb-${machine.cost}`">
      <img
        v-if="machine.img && !imgFailed"
        :src="machine.img"
        :alt="machine.name"
        class="thumb-img"
        @error="imgFailed = true"
      />
      <!-- Gradient fallback (always shown when no img or img failed) -->
      <span v-if="!machine.img || imgFailed" class="thumb-icon">{{ machine.short }}</span>
      <span class="cost-badge" :class="`badge-${machine.cost}`">{{ machine.cost }}</span>
    </div>
    <div class="machine-name" :title="machine.name">{{ machine.name }}</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  machine: { type: Object, required: true },
})

const imgFailed = ref(false)
</script>

<style scoped>
.machine-card {
  width: 90px;
  transition: transform .15s;
  position: relative;
}
.machine-card:hover { transform: translateY(-3px); }

.machine-thumb {
  width: 90px;
  height: 66px;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,.12);
}

/* Cost-based gradients (fallback background) */
.thumb-3000 { background: linear-gradient(135deg, #7b0000 0%, #c62828 40%, #ef5350 100%); }
.thumb-2500 { background: linear-gradient(135deg, #7c3500 0%, #e65100 40%, #ff9800 100%); }
.thumb-2000 { background: linear-gradient(135deg, #003060 0%, #0d47a1 40%, #42a5f5 100%); }
.thumb-1500 { background: linear-gradient(135deg, #1a3d1a 0%, #2e7d32 40%, #66bb6a 100%); }

/* Gloss overlay */
.machine-thumb::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,.18) 0%, transparent 55%, rgba(0,0,0,.2) 100%);
  pointer-events: none;
  z-index: 1;
}

.thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  position: absolute;
  inset: 0;
  z-index: 0;
}

.thumb-icon {
  font-size: 17px;
  font-weight: 900;
  color: rgba(255,255,255,.92);
  text-shadow: 0 1px 6px rgba(0,0,0,.8);
  letter-spacing: .5px;
  text-align: center;
  padding: 0 4px;
  z-index: 2;
  position: relative;
}

.cost-badge {
  position: absolute;
  bottom: 2px;
  right: 3px;
  font-size: 8px;
  font-weight: 700;
  padding: 1px 4px;
  border-radius: 3px;
  color: #fff;
  z-index: 3;
  letter-spacing: .3px;
}
.badge-3000 { background: rgba(198,40,40,.92); }
.badge-2500 { background: rgba(230,81,0,.92); }
.badge-2000 { background: rgba(13,71,161,.92); }
.badge-1500 { background: rgba(46,125,50,.92); }

.machine-name {
  font-size: 10px;
  text-align: center;
  margin-top: 4px;
  color: var(--text-primary);
  line-height: 1.3;
  word-break: break-all;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

@media (max-width: 600px) {
  .machine-card { width: 72px; }
  .machine-thumb { width: 72px; height: 52px; }
  .thumb-icon { font-size: 13px; }
  .machine-name { font-size: 9px; }
}
</style>
