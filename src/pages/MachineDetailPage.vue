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
        <div v-else-if="pageData" ref="wikiContent" class="wiki-content" v-html="pageData.content_html"></div>
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

const route = useRoute()
const id = computed(() => route.params.id)

const machine = computed(() => MACHINES.find(m => m.id === id.value) ?? null)

const loading = ref(false)
const pageData = ref(null)
const wikiContent = ref(null)
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

// pageData 变化且 DOM 更新后（flush: 'post'）绑定折叠交互
watch(pageData, (val) => {
  if (!val) return
  const root = wikiContent.value
  if (!root) return

  root.querySelectorAll('.plugin-openclose').forEach(block => {
    const link = block.querySelector('.plugin-openclose-link a')
    const content = block.querySelector('.plugin-openclose-contents')
    if (!link || !content) return

    content.style.display = 'none'
    link.textContent = '▶' + link.textContent.replace(/^[▼▶]/, '')
    link.style.cursor = 'pointer'

    link.addEventListener('click', (e) => {
      e.preventDefault()
      const open = content.style.display !== 'none'
      content.style.display = open ? 'none' : 'block'
      link.textContent = (open ? '▶' : '▼') + link.textContent.slice(1)
    })
  })
}, { flush: 'post' })

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

/* atwiki 折叠目次块 */
:deep(.plugin-openclose) {
  margin: 12px 0;
}
:deep(.plugin-openclose-link) {
  display: inline-block;
  padding: 4px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 4px;
  font-size: 13px;
  color: var(--accent);
  user-select: none;
  transition: background .15s;
}
:deep(.plugin-openclose-link:hover) {
  background: rgba(255,255,255,0.06);
}
:deep(.plugin-openclose-contents) {
  margin-top: 6px;
  border: 1px solid var(--border) !important;
  border-radius: 4px;
  padding: 12px 16px !important;
  background: var(--bg-secondary);
}

:deep(td[style*="background-color"]),
:deep(th[style*="background-color"]),
:deep(span[style*="background-color"]) {
  color: #111 !important;
}

/* 隐藏 atwiki 广告占位容器（有 min-height 但无内容，会留空白） */
:deep(.atwiki-ads-margin),
:deep([class*="atwiki_autoads"]),
:deep([id^="gpt-"]) {
  display: none !important;
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

/* wiki 内容样式 */
.wiki-content {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 28px 32px;
  line-height: 1.8;
  font-size: 14px;
  color: var(--text-primary);
}
:deep(.wiki-content h1),
:deep(.wiki-content h2),
:deep(.wiki-content h3) {
  color: var(--text-primary);
  margin: 1.2em 0 0.5em;
  font-weight: 700;
  border-bottom: 1px solid var(--border);
  padding-bottom: 4px;
}
:deep(.wiki-content table) {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
  font-size: 13px;
}
:deep(.wiki-content th),
:deep(.wiki-content td) {
  border: 1px solid var(--border);
  padding: 6px 10px;
  text-align: left;
}
:deep(.wiki-content th) {
  background: rgba(255,255,255,0.05);
  color: var(--text-primary);
  font-weight: 600;
}
:deep(.wiki-content a) {
  color: var(--accent);
  text-decoration: none;
}
:deep(.wiki-content a:hover) { text-decoration: underline; }
:deep(.wiki-content img) { max-width: 100%; border-radius: 4px; }

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
  .wiki-content { padding: 16px; }
}
</style>
