<template>
  <main class="home-page">
    <section class="overview">
      <div class="overview-main">
        <nav class="breadcrumb" aria-label="breadcrumb">
          <a href="/">EXVSDB-CN</a><span>/</span>
          <span>Tier List</span>
        </nav>

        <p class="eyebrow">INFINITE BOOST DATABASE</p>
        <h1>极限爆发机体强度 Tier 表</h1>
        <p class="lead">
          面向 EXVS.2 Infinite Boost 的中文机体资料库。按 cost 快速筛选当前环境评价，
          点击机体卡片可查看已整理的中文攻略与原始 Wiki 内容。
        </p>

        <div class="hero-actions" aria-label="cost summary">
          <button
            v-for="cost in costOptions"
            :key="cost"
            class="cost-pill"
            :class="{ active: selectedCost === String(cost) }"
            @click="selectedCost = String(cost)"
          >
            <span>{{ cost }}</span>
            <b>{{ costCounts[cost] || 0 }}</b>
          </button>
        </div>
      </div>

      <aside class="overview-panel" aria-label="selected cost overview">
        <div class="panel-top">
          <span class="panel-label">当前筛选</span>
          <strong>{{ selectedCost }} COST</strong>
        </div>

        <Transition name="panel-switch" mode="out-in">
          <div :key="selectedCost" class="panel-body">
            <div class="stat-grid">
              <div class="stat-item">
                <span>收录机体</span>
                <b>{{ animatedTotal }}</b>
              </div>
              <div class="stat-item">
                <span>S / A+ 档</span>
                <b>{{ animatedHigh }}</b>
              </div>
              <div class="stat-item">
                <span>攻略覆盖</span>
                <b>{{ animatedGuide }}</b>
              </div>
            </div>

            <div class="spotlight">
              <span class="panel-label">高评价机体</span>
              <div class="spotlight-list">
                <RouterLink
                  v-for="machine in spotlightMachines"
                  :key="machine.id"
                  class="spotlight-card"
                  :to="`/machine/${machine.id}`"
                >
                  <img :src="machine.img" :alt="machine.name" />
                  <span>{{ machine.name }}</span>
                </RouterLink>
              </div>
            </div>
          </div>
        </Transition>
      </aside>
    </section>

    <section class="rank-section">
      <div class="section-head">
        <div>
          <p class="eyebrow">RANKING BOARD</p>
          <h2>{{ selectedCost }} COST 评级表</h2>
        </div>
        <p class="update-meta">
          最后更新 <b>2026 年 4 月 22 日</b>
          <span>Ver.2.40</span>
        </p>
      </div>

      <CostFilter v-model="selectedCost" />
      <Transition name="tier-switch" mode="out-in">
        <TierTable :key="selectedCost" :machines="filteredMachines" />
      </Transition>
    </section>
  </main>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { MACHINES } from '../data/machines.js'
import CostFilter from '../components/CostFilter.vue'
import TierTable from '../components/TierTable.vue'

const selectedCost = ref('3000')
const costOptions = [3000, 2500, 2000, 1500]
const topTiers = ['S', 'A+']

const filteredMachines = computed(() =>
  MACHINES.filter(m => String(m.cost) === selectedCost.value)
)

const costCounts = computed(() =>
  MACHINES.reduce((counts, machine) => {
    counts[machine.cost] = (counts[machine.cost] || 0) + 1
    return counts
  }, {})
)

const highTierCount = computed(() =>
  filteredMachines.value.filter(machine => topTiers.includes(machine.tier)).length
)

const guideCount = computed(() =>
  filteredMachines.value.filter(machine => Boolean(machine.link)).length
)

const animatedTotal = ref(0)
const animatedHigh  = ref(0)
const animatedGuide = ref(0)

function animateCounter(target, to, duration = 550) {
  if (typeof requestAnimationFrame === 'undefined') {
    target.value = to
    return
  }
  const start = performance.now()
  const tick = (now) => {
    const t = Math.min((now - start) / duration, 1)
    const eased = 1 - Math.pow(1 - t, 3)
    target.value = Math.round(to * eased)
    if (t < 1) requestAnimationFrame(tick)
  }
  requestAnimationFrame(tick)
}

watch(selectedCost, () => {
  animateCounter(animatedTotal, filteredMachines.value.length)
  animateCounter(animatedHigh,  highTierCount.value)
  animateCounter(animatedGuide, guideCount.value)
}, { immediate: true })

const spotlightMachines = computed(() => {
  const ranked = filteredMachines.value.filter(machine => topTiers.includes(machine.tier))
  return (ranked.length ? ranked : filteredMachines.value).slice(0, 4)
})
</script>

<style scoped>
.home-page {
  max-width: 1280px;
  margin: 0 auto;
  padding: 28px 24px 80px;
}

.overview {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 380px;
  gap: 28px;
  align-items: stretch;
  margin-bottom: 34px;
}

.overview-main {
  min-height: 330px;
  padding: 28px 0 26px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.breadcrumb {
  font-size: 11px;
  color: var(--text-muted);
  margin-bottom: 36px;
  letter-spacing: .6px;
}

.breadcrumb a {
  color: var(--accent);
  opacity: .85;
  transition: opacity .15s;
}

.breadcrumb a:hover { opacity: 1; }
.breadcrumb span { margin-left: 8px; opacity: .55; }

.eyebrow {
  font-family: var(--font-ui);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--accent);
  margin-bottom: 8px;
}

h1 {
  max-width: 760px;
  font-size: 42px;
  line-height: 1.18;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.lead {
  max-width: 720px;
  color: var(--text-muted);
  font-size: 15px;
  line-height: 1.9;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 30px;
}

.cost-pill {
  min-width: 104px;
  height: 42px;
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 0 13px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-muted);
  transition: border-color .15s, background .15s, color .15s, transform .15s;
}

.cost-pill:hover,
.cost-pill.active {
  border-color: var(--accent);
  background: var(--bg-card);
  color: var(--text-primary);
  transform: translateY(-1px);
}

.cost-pill span {
  font-family: var(--font-ui);
  font-size: 18px;
  font-weight: 700;
}

.cost-pill b {
  min-width: 28px;
  height: 22px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 3px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: var(--font-ui);
  font-size: 13px;
}

.overview-panel {
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg-secondary);
  padding: 20px;
  box-shadow: 0 18px 42px rgba(0,0,0,.22);
}

.panel-top {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.panel-label {
  display: block;
  color: var(--text-muted);
  font-size: 11px;
  letter-spacing: .8px;
}

.panel-top strong {
  font-family: var(--font-ui);
  font-size: 28px;
  line-height: 1;
  color: var(--text-primary);
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 18px;
}

.stat-item {
  padding: 13px 10px;
  background: var(--bg-card);
  border-right: 1px solid var(--border);
}

.stat-item:last-child { border-right: none; }

.stat-item span {
  display: block;
  color: var(--text-muted);
  font-size: 11px;
  margin-bottom: 4px;
  white-space: nowrap;
}

.stat-item b {
  font-family: var(--font-ui);
  font-size: 26px;
  line-height: 1;
  color: var(--text-primary);
}

.spotlight-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-top: 9px;
}

.spotlight-card {
  min-height: 86px;
  position: relative;
  overflow: hidden;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--bg-primary);
}

.spotlight-card img {
  width: 100%;
  height: 100%;
  min-height: 86px;
  object-fit: cover;
  display: block;
  opacity: .86;
  transition: transform .18s, opacity .18s;
}

.spotlight-card span {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 20px 8px 7px;
  background: linear-gradient(180deg, transparent 0%, rgba(0,0,0,.78) 72%);
  color: #fff;
  font-size: 11px;
  line-height: 1.35;
  text-shadow: 0 1px 6px rgba(0,0,0,.85);
}

.spotlight-card:hover img {
  transform: scale(1.05);
  opacity: 1;
}

.rank-section {
  margin-top: 8px;
}

.section-head {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 14px;
}

h2 {
  font-size: 24px;
  line-height: 1.25;
  color: var(--text-primary);
}

.update-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-muted);
  font-size: 12px;
  white-space: nowrap;
}

.update-meta b {
  color: var(--text-primary);
  font-weight: 600;
}

.update-meta span {
  color: var(--accent);
  font-family: var(--font-ui);
  font-weight: 700;
  letter-spacing: .8px;
}

/* TierTable 切换动效 */
.tier-switch-leave-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.tier-switch-enter-active { transition: opacity 0.22s ease, transform 0.22s ease; }
.tier-switch-leave-to  { opacity: 0; transform: translateY(-6px); }
.tier-switch-enter-from { opacity: 0; transform: translateY(10px); }

/* 右侧面板数据切换动效 */
.panel-switch-leave-active { transition: opacity 0.12s ease; }
.panel-switch-enter-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.panel-switch-leave-to  { opacity: 0; }
.panel-switch-enter-from { opacity: 0; transform: translateY(6px); }

@media (max-width: 900px) {
  .overview {
    grid-template-columns: 1fr;
    gap: 18px;
  }

  .overview-main {
    min-height: auto;
    padding-bottom: 0;
  }

  .breadcrumb {
    margin-bottom: 24px;
  }

  .section-head {
    align-items: flex-start;
    flex-direction: column;
  }

  .update-meta {
    white-space: normal;
  }
}

@media (max-width: 600px) {
  .home-page {
    padding: 18px 14px 60px;
  }

  h1 {
    font-size: 29px;
  }

  .lead {
    font-size: 13px;
  }

  .hero-actions {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .cost-pill {
    width: 100%;
  }

  .overview-panel {
    padding: 14px;
  }

  .stat-grid {
    grid-template-columns: 1fr;
  }

  .stat-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-right: none;
    border-bottom: 1px solid var(--border);
  }

  .stat-item:last-child {
    border-bottom: none;
  }

  .spotlight-list {
    grid-template-columns: 1fr;
  }
}
</style>
