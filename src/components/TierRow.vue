<template>
  <div class="tier-row" :class="meta.cls">
    <div class="tier-label" :class="meta.cls">
      <span class="tier-letter">{{ meta.label }}</span>
      <span v-if="meta.sub" class="tier-sub">{{ meta.sub }}</span>
    </div>
    <div class="tier-content">
      <template v-if="machines.length > 0">
        <MachineCard
          v-for="(m, index) in machines"
          :key="m.id"
          :machine="m"
          :tier-cls="meta.cls"
          :style="{ '--card-delay': `${index * 45}ms` }"
        />
      </template>
      <span v-else class="empty-msg">— 暂无机体 —</span>
    </div>
  </div>
</template>

<script setup>
import MachineCard from './MachineCard.vue'

defineProps({
  meta:     { type: Object,  required: true },
  machines: { type: Array,   default: () => [] },
})
</script>

<style scoped>
.tier-row {
  display: flex;
  border-bottom: 1px solid var(--border);
  min-height: 90px;
  transition: background .15s;
}
.tier-row:last-child { border-bottom: none; }

/* tier-aware left glow on the content area */
.tier-row.s      { --row-glow: rgba(232, 21,  21,  0.5); }
.tier-row.aplus  { --row-glow: rgba(249, 128,  0,  0.4); }
.tier-row.a      { --row-glow: rgba(230, 176,  0,  0.38); }
.tier-row.aminus { --row-glow: rgba(168, 196,  0,  0.38); }
.tier-row.bplus  { --row-glow: rgba( 34, 192, 96,  0.4); }
.tier-row.b      { --row-glow: rgba( 30, 144, 232, 0.4); }
.tier-row.bminus { --row-glow: rgba(102,  68, 204, 0.4); }
.tier-row.c      { --row-glow: rgba( 90, 104, 117, 0.28); }

.tier-label {
  min-width: 84px;
  width: 84px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  flex-shrink: 0;
  user-select: none;
  position: relative;
}

/* right-edge shadow for depth */
.tier-label::after {
  content: '';
  position: absolute;
  right: 0; top: 0; bottom: 0;
  width: 1px;
  background: rgba(0,0,0,0.4);
}

.tier-letter {
  font-family: var(--font-ui);
  font-size: 36px;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 2px 12px rgba(0,0,0,0.7);
  line-height: 1;
  letter-spacing: 1px;
}

.tier-sub {
  font-family: var(--font-ui);
  font-size: 9px;
  font-weight: 600;
  margin-top: 3px;
  letter-spacing: 1px;
  opacity: .75;
  color: #fff;
}

/* Tier label colours — rainbow gradient: red → orange → yellow → chartreuse → green → blue → purple → gray */
.tier-label.s      { background: linear-gradient(160deg, #e81515 0%, #990000 100%); box-shadow: inset -4px 0 16px rgba(0,0,0,0.3), 0 0 24px rgba(232,21,21,0.25); }
.tier-label.aplus  { background: linear-gradient(160deg, #f98000 0%, #b55500 100%); box-shadow: inset -4px 0 16px rgba(0,0,0,0.3); }
.tier-label.a      { background: linear-gradient(160deg, #e6b000 0%, #9c7400 100%); box-shadow: inset -4px 0 16px rgba(0,0,0,0.3); }
.tier-label.aminus { background: linear-gradient(160deg, #a8c400 0%, #6a7c00 100%); box-shadow: inset -4px 0 16px rgba(0,0,0,0.3); }
.tier-label.bplus  { background: linear-gradient(160deg, #22c060 0%, #107838 100%); box-shadow: inset -4px 0 16px rgba(0,0,0,0.3); }
.tier-label.b      { background: linear-gradient(160deg, #1e90e8 0%, #0d58a8 100%); box-shadow: inset -4px 0 16px rgba(0,0,0,0.3); }
.tier-label.bminus { background: linear-gradient(160deg, #6644cc 0%, #3a2888 100%); box-shadow: inset -4px 0 16px rgba(0,0,0,0.3); }
.tier-label.c      { background: linear-gradient(160deg, #5a6875 0%, #363d43 100%); box-shadow: inset -4px 0 16px rgba(0,0,0,0.3); }

.tier-content {
  flex: 1;
  padding: 8px 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-content: flex-start;
  background: var(--bg-secondary);
  box-shadow: var(--tier-content-shadow, inset 4px 0 12px var(--row-glow, transparent));
}

.tier-row.alt .tier-content { background: var(--bg-card); }

.empty-msg {
  color: var(--text-muted);
  font-size: 11px;
  font-family: var(--font-ui);
  letter-spacing: 2px;
  padding: 28px 0;
  display: block;
  opacity: 0.5;
}

@media (max-width: 600px) {
  .tier-label { min-width: 46px; width: 46px; }
  .tier-letter { font-size: 22px; }
}
</style>
