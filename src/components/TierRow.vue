<template>
  <div class="tier-row">
    <div class="tier-label" :class="meta.cls">
      {{ meta.label }}
      <span v-if="meta.sub" class="tier-sub">{{ meta.sub }}</span>
    </div>
    <div class="tier-content">
      <template v-if="machines.length > 0">
        <MachineCard v-for="m in machines" :key="m.id" :machine="m" />
      </template>
      <span v-else class="empty-msg">（該当機体なし）</span>
    </div>
  </div>
</template>

<script setup>
import MachineCard from './MachineCard.vue'

defineProps({
  meta:     { type: Object,  required: true },  // { label, sub, cls }
  machines: { type: Array,   default: () => [] },
})
</script>

<style scoped>
.tier-row {
  display: flex;
  border-bottom: 1px solid var(--border);
  min-height: 100px;
}
.tier-row:last-child { border-bottom: none; }

.tier-label {
  min-width: 60px;
  width: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  font-size: 26px;
  font-weight: 900;
  color: #fff;
  text-shadow: 0 1px 6px rgba(0,0,0,.6);
  flex-shrink: 0;
  user-select: none;
}
.tier-sub {
  font-size: 9px;
  font-weight: 400;
  margin-top: 2px;
  letter-spacing: .5px;
  opacity: .85;
}

/* Tier label colours */
.tier-label.s     { background: linear-gradient(160deg, #ff1a1a 0%, #c00 100%); }
.tier-label.aplus { background: linear-gradient(160deg, #ff9900 0%, #c76400 100%); }
.tier-label.a     { background: linear-gradient(160deg, #e6b800 0%, #9c7a00 100%); }
.tier-label.bplus { background: linear-gradient(160deg, #2ebf6e 0%, #1a8a4a 100%); }
.tier-label.b     { background: linear-gradient(160deg, #3a8ee6 0%, #1a5fa8 100%); }
.tier-label.c     { background: linear-gradient(160deg, #6c757d 0%, #464d52 100%); }

.tier-content {
  flex: 1;
  padding: 8px 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  align-content: flex-start;
  background: var(--bg-secondary);
}

/* alternate row background via :nth-child handled in TierTable via class */
.tier-row.alt .tier-content { background: var(--bg-card); }

.empty-msg {
  color: var(--text-muted);
  font-size: 12px;
  padding: 20px 0;
  display: block;
}

@media (max-width: 600px) {
  .tier-label { min-width: 44px; width: 44px; font-size: 20px; }
}
</style>
