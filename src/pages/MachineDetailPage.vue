<template>
  <main class="detail-page">
    <nav class="breadcrumb">
      <RouterLink to="/">首页</RouterLink><span>›</span>
      <span>{{ machine ? machine.name : id }}</span>
    </nav>

    <div v-if="!machine" class="not-found">
      <p>未找到机体 <code>{{ id }}</code></p>
      <RouterLink to="/" class="back-btn">← 返回首页</RouterLink>
    </div>

    <template v-else>
      <!-- 语言切换（仅当中文版存在时显示） -->
      <div v-if="hasZh" class="toolbar">
        <div class="lang-toggle">
          <button :class="{ active: lang === 'zh' }" @click="setLang('zh')">中文</button>
          <button :class="{ active: lang === 'ja' }" @click="setLang('ja')">日文</button>
        </div>
      </div>

      <!-- 攻略内容 -->
      <div class="content-section">
        <div v-if="loading" class="status-box">加载中…</div>
        <WikiContent v-else-if="pageData"
          :nodes="pageData.content_nodes ?? null"
          :html="pageData.content_nodes ? null : pageData.content_html"
        />
        <div v-else class="status-box no-data">
          <p>暂无攻略内容</p>
          <a v-if="machine.link" :href="machine.link" target="_blank" rel="noopener noreferrer" class="ext-btn">
            查看原版攻略 ↗
          </a>
        </div>
      </div>

      <RouterLink to="/" class="back-btn">← 返回Tier表</RouterLink>
    </template>
  </main>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { MACHINES } from '../data/machines.js'
import WikiContent from '../components/WikiContent.vue'

const route = useRoute()
const id = computed(() => route.params.id)

const machine = computed(() => MACHINES.find(m => m.id === id.value) ?? null)

const loading = ref(false)
const pageData = ref(null)
const lang = ref('zh')   // 当前语言
const hasZh = ref(false) // 是否存在中文版

async function loadPageData(machineId) {
  loading.value = true
  pageData.value = null
  try {
    const zhRes = await fetch(`/data/machines/${machineId}_zh.json`)
    hasZh.value = zhRes.ok
    if (!hasZh.value) lang.value = 'ja'

    const url = lang.value === 'zh' && hasZh.value
      ? `/data/machines/${machineId}_zh.json`
      : `/data/machines/${machineId}.json`
    const res = await fetch(url)
    if (res.ok) pageData.value = await res.json()
  } catch {
    // silently show "no data" state
  } finally {
    loading.value = false
  }
}

async function setLang(newLang) {
  if (newLang === lang.value) return
  lang.value = newLang
  await loadPageData(id.value)
}

onMounted(() => loadPageData(id.value))
watch(id, (newId) => loadPageData(newId))
</script>

<style scoped>
.detail-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 24px 24px 80px;
}

.breadcrumb {
  font-size: 11px;
  color: var(--text-muted);
  margin-bottom: 24px;
  letter-spacing: .5px;
}
.breadcrumb a { color: var(--accent); opacity: .8; text-decoration: none; transition: opacity .15s; }
.breadcrumb a:hover { opacity: 1; }
.breadcrumb span { margin: 0 6px; opacity: .4; }


.toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 12px;
}
.lang-toggle {
  display: flex;
  gap: 2px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 3px;
}
.lang-toggle button {
  padding: 4px 14px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: var(--text-muted);
  font-size: 12px;
  cursor: pointer;
  transition: background .15s, color .15s;
}
.lang-toggle button.active {
  background: var(--accent);
  color: #fff;
}
.lang-toggle button:not(.active):hover {
  background: rgba(255,255,255,0.06);
  color: var(--text-primary);
}

/* 内容区 */
.content-section {
  margin-bottom: 32px;
}

.status-box {
  padding: 40px 24px;
  text-align: center;
  background: var(--bg-secondary);
  border-radius: 8px;
  border: 1px solid var(--border);
  color: var(--text-muted);
  font-size: 14px;
}
.no-data .hint {
  font-size: 12px;
  margin-top: 8px;
  opacity: .7;
}
.no-data code {
  background: rgba(255,255,255,0.08);
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
}

.ext-btn {
  display: inline-block;
  margin-top: 16px;
  padding: 8px 20px;
  background: var(--accent);
  color: #fff;
  border-radius: 5px;
  text-decoration: none;
  font-size: 13px;
  font-weight: 600;
  transition: opacity .15s;
}
.ext-btn:hover { opacity: .85; }

/* 返回按钮 */
.back-btn {
  display: inline-block;
  color: var(--accent);
  text-decoration: none;
  font-size: 13px;
  opacity: .8;
  transition: opacity .15s;
}
.back-btn:hover { opacity: 1; }

.not-found {
  padding: 60px 24px;
  text-align: center;
  color: var(--text-muted);
}

@media (max-width: 600px) {
  .machine-header {
    flex-direction: column;
    gap: 16px;
  }
  .machine-thumb {
    width: 100%;
    height: 72px;
  }
  .machine-name { font-size: 20px; }
}
</style>
