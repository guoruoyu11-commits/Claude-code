<template>
  <a
    class="machine-card"
    :class="`tier-${tierCls}`"
    :href="machine.link || undefined"
    :target="machine.link ? '_blank' : undefined"
    rel="noopener noreferrer"
  >
    <div class="machine-thumb" :class="`thumb-${machine.cost}`">
      <img
        v-if="machine.img && !imgFailed"
        :src="machine.img"
        :alt="machine.name"
        class="thumb-img"
        @error="imgFailed = true"
      />
      <span v-if="!machine.img || imgFailed" class="thumb-icon">{{ machine.short }}</span>
      <span class="cost-badge" :class="`badge-${machine.cost}`">{{ machine.cost }}</span>
    </div>
    <div class="machine-name" :title="machine.name">{{ machine.name }}</div>
  </a>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  machine: { type: Object, required: true },
  tierCls: { type: String, default: '' },
})

const imgFailed = ref(false)
</script>

<style scoped>
.machine-card {
  width: 148px;
  position: relative;
  cursor: pointer;
  display: inline-block;
  text-decoration: none;
  transition: transform .18s ease, filter .18s ease;
}
.machine-card:hover {
  transform: translateY(-4px) scale(1.02);
  z-index: 2;
}

/* tier-aware glow on hover */
.machine-card.tier-s:hover      .machine-thumb { box-shadow: 0 6px 20px rgba(255,40,40,0.5), 0 0 0 1px rgba(255,40,40,0.4); }
.machine-card.tier-aplus:hover  .machine-thumb { box-shadow: 0 6px 20px rgba(255,140,0,0.45), 0 0 0 1px rgba(255,140,0,0.4); }
.machine-card.tier-a:hover      .machine-thumb { box-shadow: 0 6px 20px rgba(220,185,0,0.45), 0 0 0 1px rgba(220,185,0,0.35); }
.machine-card.tier-aminus:hover .machine-thumb { box-shadow: 0 6px 20px rgba(168,196,0,0.45),  0 0 0 1px rgba(168,196,0,0.35); }
.machine-card.tier-bplus:hover  .machine-thumb { box-shadow: 0 6px 20px rgba(34,192,96,0.45),  0 0 0 1px rgba(34,192,96,0.4); }
.machine-card.tier-b:hover      .machine-thumb { box-shadow: 0 6px 20px rgba(30,144,232,0.45),  0 0 0 1px rgba(30,144,232,0.4); }
.machine-card.tier-bminus:hover .machine-thumb { box-shadow: 0 6px 20px rgba(102,68,204,0.5),   0 0 0 1px rgba(102,68,204,0.4); }
.machine-card.tier-c:hover      .machine-thumb { box-shadow: 0 6px 20px rgba(100,120,140,0.35), 0 0 0 1px rgba(100,120,140,0.3); }

.machine-thumb {
  width: 148px;
  height: 64px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.08);
  transition: box-shadow .18s ease;
}

/* Cost-based gradients (fallback background) */
.thumb-3000 { background: linear-gradient(135deg, #5a0000 0%, #b02020 50%, #d94040 100%); }
.thumb-2500 { background: linear-gradient(135deg, #5c2800 0%, #c55000 50%, #e87020 100%); }
.thumb-2000 { background: linear-gradient(135deg, #001c45 0%, #0b3a8a 50%, #2a6acc 100%); }
.thumb-1500 { background: linear-gradient(135deg, #0f2a0f 0%, #206020 50%, #3a9040 100%); }

/* Gloss overlay */
.machine-thumb::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(145deg, rgba(255,255,255,0.12) 0%, transparent 50%, rgba(0,0,0,0.25) 100%);
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
  font-family: var(--font-ui);
  font-size: 16px;
  font-weight: 700;
  color: rgba(255,255,255,.85);
  text-shadow: 0 1px 8px rgba(0,0,0,0.9);
  letter-spacing: .5px;
  z-index: 2;
  position: relative;
}

.cost-badge {
  position: absolute;
  bottom: 2px;
  right: 3px;
  font-family: var(--font-ui);
  font-size: 10px;
  font-weight: 700;
  padding: 1px 4px;
  border-radius: 2px;
  color: rgba(255,255,255,0.9);
  z-index: 3;
  letter-spacing: .5px;
}
.badge-3000 { background: rgba(180,30,30,0.88); }
.badge-2500 { background: rgba(200,70,0,0.88); }
.badge-2000 { background: rgba(15,60,150,0.88); }
.badge-1500 { background: rgba(35,105,45,0.88); }

.machine-name {
  font-size: 12px;
  text-align: center;
  margin-top: 5px;
  color: var(--text-primary);
  line-height: 1.35;
  word-break: break-all;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  opacity: 0.85;
  transition: opacity .15s;
}
.machine-card:hover .machine-name { opacity: 1; }

@media (max-width: 600px) {
  .machine-card { width: 105px; }
  .machine-thumb { width: 105px; height: 45px; }
  .thumb-icon { font-size: 12px; }
  .machine-name { font-size: 10px; }
}
</style>
