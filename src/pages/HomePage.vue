<template>
  <main>
    <nav class="breadcrumb" aria-label="breadcrumb">
      <a href="/">EXVSDB</a><span>›</span>
      <span>Tier 表</span>
    </nav>

    <div class="title-block">
      <h1>【2026年4月最新】极限爆发 机体强度·Tier 表</h1>
      <p class="update-meta">
        最后更新：<b>2026年4月12日</b>
        <span class="meta-sep">|</span>
        适用版本：极限爆发 Ver.2.40
      </p>
    </div>

    <div class="desc-box">
      高达 EXVS.2 极限爆发（INF-B）的<b>机体强度·Tier 表</b>。<br />
      基于对战胜率、使用率及高端玩家战绩进行独立评级。
      可通过费用标签筛选查看，等级仅供参考。
    </div>

    <CostFilter v-model="selectedCost" />
    <TierTable :machines="filteredMachines" />
  </main>
</template>

<script setup>
import { ref, computed } from 'vue'
import { MACHINES } from '../data/machines.js'
import CostFilter from '../components/CostFilter.vue'
import TierTable  from '../components/TierTable.vue'

const selectedCost = ref('3000')

const filteredMachines = computed(() =>
  MACHINES.filter(m => String(m.cost) === selectedCost.value)
)
</script>

<style scoped>
main {
  max-width: 1280px;
  margin: 0 auto;
  padding: 24px 24px 80px;
}

.breadcrumb {
  font-size: 11px;
  color: var(--text-muted);
  margin-bottom: 18px;
  letter-spacing: .5px;
}
.breadcrumb a { color: var(--accent); opacity: .8; transition: opacity .15s; }
.breadcrumb a:hover { opacity: 1; }
.breadcrumb span { margin: 0 6px; opacity: .4; }

.title-block { margin-bottom: 16px; }

h1 {
  font-size: 23px;
  font-weight: 700;
  line-height: 1.4;
  margin-bottom: 6px;
  color: var(--text-primary);
}

.update-meta {
  font-size: 11px;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 0;
}
.update-meta b { color: #a8c4d8; font-weight: 600; }
.meta-sep { margin: 0 10px; opacity: .35; }

.desc-box {
  background: var(--bg-secondary);
  border-left: 2px solid var(--accent);
  border-radius: 0 5px 5px 0;
  padding: 11px 16px;
  font-size: 12.5px;
  color: var(--text-muted);
  line-height: 1.75;
  margin-bottom: 24px;
  box-shadow: inset 4px 0 14px rgba(232,51,42,0.06);
}
.desc-box b { color: var(--text-primary); }

@media (max-width: 600px) {
  h1 { font-size: 16px; }
  main { padding: 16px 14px 60px; }
}
</style>
