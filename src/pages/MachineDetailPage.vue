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
      <!-- 工具栏：子页面 tab + 右侧语言切换 + Wiki 链接 -->
      <div v-if="subPages.length || hasZh || machine.link" class="toolbar">
        <!-- 左：子页面 tab -->
        <div v-if="subPages.length" class="sub-page-nav">
          <button :class="{ active: currentSub === null }" @click="selectSub(null)">综合解说</button>
          <button v-for="sp in subPages" :key="sp.file"
            :class="{ active: currentSub === sp.file }"
            @click="selectSub(sp.file)">{{ sp.name }}</button>
        </div>
        <!-- 右：语言切换 + Wiki 链接 -->
        <div class="toolbar-right">
          <div v-if="hasZh" class="lang-toggle">
            <button :class="{ active: lang === 'zh' }" @click="setLang('zh')">中文</button>
            <button :class="{ active: lang === 'ja' }" @click="setLang('ja')">日文</button>
          </div>
          <a v-if="machine.link" :href="machine.link" target="_blank" rel="noopener noreferrer" class="wiki-link">
            参考原Wiki ↗
          </a>
        </div>
      </div>

      <!-- 攻略内容 -->
      <div class="content-section">
        <!-- Left sidebar: machine list by cost -->
        <aside class="machine-nav-sidebar">
          <div class="sidebar-inner">
            <div class="sidebar-title">机体目录</div>
            <div v-for="group in costGroups" :key="group.cost" class="cost-group">
              <button class="cost-heading" @click="toggleCostGroup(group.cost)">
                <span class="cost-label">{{ group.cost }} COST</span>
                <span class="toggle-arrow" :class="{ collapsed: sidebarCollapsed[group.cost] }">▾</span>
              </button>
              <Transition name="expand">
                <ul v-if="!sidebarCollapsed[group.cost]" class="machine-list">
                  <li v-for="m in group.machines" :key="m.id">
                    <RouterLink
                      :to="`/machine/${m.id}`"
                      class="machine-link"
                      :class="{ active: m.id === id }"
                    >{{ m.name }}</RouterLink>
                  </li>
                </ul>
              </Transition>
            </div>
          </div>
        </aside>

        <Transition name="wiki-switch" mode="out-in">
          <div v-if="loading" key="loading" class="status-box">加载中…</div>
          <div v-else-if="pageData" :key="pageKey" class="detail-layout">
            <WikiContent
              :nodes="mainNodes"
              :html="mainNodes === null ? (pageData.content_html ?? null) : null"
              :sub-pages="subPages"
              :parent-url="machine.link"
              :machine-id="id"
              @select-sub="selectSub"
            />
            <aside v-if="infoboxNode" class="infobox-sidebar">
              <WikiContent :nodes="[infoboxNode]" :machine-id="id" />
            </aside>
          </div>
          <div v-else key="empty" class="status-box no-data">
            <p>暂无攻略内容</p>
            <a v-if="machine.link" :href="machine.link" target="_blank" rel="noopener noreferrer" class="ext-btn">
              查看原版攻略 ↗
            </a>
          </div>
        </Transition>
      </div>

      <RouterLink to="/" class="back-btn">← 返回Tier表</RouterLink>
    </template>
  </main>

  <button v-show="showTop" class="back-to-top" @click="scrollToTop" aria-label="返回顶部">↑</button>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { MACHINES } from '../data/machines.js'
import WikiContent from '../components/WikiContent.vue'

const COST_ORDER = [3000, 2500, 2000, 1500]
const costGroups = computed(() =>
  COST_ORDER.map(c => ({ cost: c, machines: MACHINES.filter(m => m.cost === c) }))
)
const sidebarCollapsed = ref({ 3000: true, 2500: true, 2000: true, 1500: true })
function toggleCostGroup(cost) {
  sidebarCollapsed.value[cost] = !sidebarCollapsed.value[cost]
}

const route = useRoute()
const router = useRouter()
const id = computed(() => route.params.id)

const machine = computed(() => MACHINES.find(m => m.id === id.value) ?? null)

const loading = ref(false)
const pageData = ref(null)
const lang = ref('zh')
const hasZh = ref(false)
const subPages = ref([])   // 子页面列表（从主页面数据读取）
const currentSub = ref(null) // null = 主页面，否则为子页面 file ID
const infoboxNode = ref(null) // 主页面 infobox，切换子页面时保留

function extractInfobox(nodes) {
  if (!nodes) return null
  return nodes.find(n =>
    n?.t === 'div' &&
    typeof n?.a?.class === 'string' &&
    n.a.class.includes('float-right')
  ) ?? null
}

const pageKey = computed(() => `${id.value}__${currentSub.value ?? 'main'}__${lang.value}`)

const mainNodes = computed(() => {
  const nodes = pageData.value?.content_nodes
  if (!nodes) return null
  const ib = extractInfobox(nodes)
  return ib ? nodes.filter(n => n !== ib) : nodes
})

async function loadPageData(machineId, checkHasZh = true) {
  loading.value = true
  pageData.value = null
  currentSub.value = null
  subPages.value = []
  infoboxNode.value = null
  try {
    let data
    if (checkHasZh) {
      const zhRes = await fetch(`/data/machines/${machineId}_zh.json`)
      hasZh.value = zhRes.ok
      if (!hasZh.value) lang.value = 'ja'
      if (lang.value === 'zh') data = await zhRes.json()
    } else if (lang.value === 'zh' && hasZh.value) {
      const zhRes = await fetch(`/data/machines/${machineId}_zh.json`)
      if (zhRes.ok) data = await zhRes.json()
    }
    if (!data) {
      const res = await fetch(`/data/machines/${machineId}.json`)
      if (res.ok) data = await res.json()
    }
    if (data) {
      pageData.value = data
      subPages.value = data.sub_pages || []
      infoboxNode.value = extractInfobox(data.content_nodes)
    }
  } catch {
    // silently show "no data" state
  } finally {
    loading.value = false
  }
}

async function loadSubContent(fileId) {
  loading.value = true
  pageData.value = null
  try {
    let data
    if (lang.value === 'zh') {
      const zhRes = await fetch(`/data/machines/${fileId}_zh.json`)
      if (zhRes.ok) data = await zhRes.json()
    }
    if (!data) {
      const res = await fetch(`/data/machines/${fileId}.json`)
      if (res.ok) data = await res.json()
    }
    if (data) pageData.value = data
  } catch {
    // no data
  } finally {
    loading.value = false
  }
}

async function selectSub(fileId) {
  if (currentSub.value === fileId) return
  currentSub.value = fileId
  router.replace({ query: fileId ? { sub: fileId } : {} })
  if (fileId === null) await loadPageData(id.value)
  else await loadSubContent(fileId)
}

async function setLang(newLang) {
  if (newLang === lang.value) return
  lang.value = newLang
  if (currentSub.value) {
    // 刷新主页面的 sub_pages（更新 tab 名称）
    try {
      const mainUrl = newLang === 'zh' && hasZh.value
        ? `/data/machines/${id.value}_zh.json`
        : `/data/machines/${id.value}.json`
      const res = await fetch(mainUrl)
      if (res.ok) subPages.value = (await res.json()).sub_pages || []
    } catch {}
    await loadSubContent(currentSub.value)
  } else {
    await loadPageData(id.value, false)
  }
}

const showTop = ref(false)
function onScroll() { showTop.value = window.scrollY > 300 }
function scrollToTop() { window.scrollTo({ top: 0, behavior: 'smooth' }) }

onMounted(async () => {
  await loadPageData(id.value)
  const subFromQuery = route.query.sub
  if (subFromQuery && subPages.value.some(sp => sp.file === subFromQuery)) {
    currentSub.value = subFromQuery
    await loadSubContent(subFromQuery)
  }
  window.addEventListener('scroll', onScroll, { passive: true })
})
onUnmounted(() => window.removeEventListener('scroll', onScroll))
watch(id, (newId) => loadPageData(newId))

watch(machine, (m) => {
  if (m) sidebarCollapsed.value[m.cost] = false
}, { immediate: true })
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
  align-items: center;
  border-bottom: 1px solid var(--border);
  margin-bottom: 20px;
}

/* 左：下划线风格子页面 tab */
.sub-page-nav {
  display: flex;
  align-items: stretch;
}
.sub-page-nav button {
  padding: 10px 18px;
  border: none;
  border-bottom: 2px solid transparent;
  background: transparent;
  color: var(--text-muted);
  font-size: 13px;
  cursor: pointer;
  transition: color .15s, border-color .15s;
  margin-bottom: -1px;
}
.sub-page-nav button.active {
  color: var(--accent);
  border-bottom-color: var(--accent);
}
.sub-page-nav button:not(.active):hover { color: var(--text-primary); }

/* 右：语言切换 + wiki 链接 */
.toolbar-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 6px;
}
.lang-toggle {
  display: flex;
  gap: 2px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 5px;
  padding: 2px;
}
.lang-toggle button {
  padding: 3px 12px;
  border: none;
  border-radius: 3px;
  background: transparent;
  color: var(--text-muted);
  font-size: 12px;
  cursor: pointer;
  transition: background .15s, color .15s;
}
.lang-toggle button.active { background: var(--accent); color: #fff; }
.lang-toggle button:not(.active):hover { color: var(--text-primary); }

.wiki-link {
  font-size: 12px;
  color: var(--text-muted);
  text-decoration: none;
  transition: color .15s;
}
.wiki-link:hover { color: var(--accent); }

/* 内容区 */
.content-section {
  position: relative;
  margin-bottom: 32px;
  font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-size: 15px;
  line-height: 1.9;
  letter-spacing: 0.02em;
}

/* Left sidebar */
.machine-nav-sidebar {
  display: none;
  position: absolute;
  right: calc(100% + 20px);
  top: 0;
  width: 200px;
  height: 100%;
}

@media (min-width: 1220px) {
  .machine-nav-sidebar { display: block; }
}

.sidebar-inner {
  position: sticky;
  top: 80px;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 8px;
  scrollbar-width: thin;
  scrollbar-color: var(--border) transparent;
}

.sidebar-title {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .08em;
  color: var(--text-muted);
  text-transform: uppercase;
  margin-bottom: 10px;
  padding: 0 4px;
}

.cost-group {
  margin-bottom: 4px;
}

.cost-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  background: none;
  border: none;
  padding: 5px 6px;
  border-radius: 4px;
  cursor: pointer;
  color: var(--text-primary);
  font-size: 12px;
  font-weight: 600;
  transition: background .12s;
}
.cost-heading:hover { background: rgba(255,255,255,0.06); }

.cost-label { opacity: .85; }

.toggle-arrow {
  font-size: 11px;
  opacity: .55;
  display: inline-block;
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.15s;
}
.toggle-arrow.collapsed { transform: rotate(-90deg); }
.cost-heading:hover .toggle-arrow { opacity: .85; }

/* expand/collapse transition */
.expand-enter-active,
.expand-leave-active {
  overflow: hidden;
  transition: max-height 0.32s cubic-bezier(0.4, 0, 0.2, 1),
              opacity 0.25s ease;
}
.expand-enter-from,
.expand-leave-to {
  max-height: 0 !important;
  opacity: 0;
}
.expand-enter-to,
.expand-leave-from {
  max-height: 2400px;
  opacity: 1;
}

.machine-list {
  list-style: none;
  padding: 0;
  margin: 2px 0 6px;
}

.machine-link {
  display: block;
  padding: 3px 6px 3px 14px;
  font-size: 12px;
  color: var(--text-muted);
  text-decoration: none;
  border-radius: 3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color .12s, background .12s;
  line-height: 1.5;
}
.machine-link:hover { color: var(--text-primary); background: rgba(255,255,255,0.05); }
.machine-link.active {
  color: var(--accent);
  font-weight: 600;
  background: color-mix(in srgb, var(--accent) 10%, transparent);
}

.wiki-switch-leave-active { transition: opacity 0.12s ease, transform 0.12s ease; }
.wiki-switch-enter-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.wiki-switch-leave-to   { opacity: 0; transform: translateY(-5px); }
.wiki-switch-enter-from { opacity: 0; transform: translateY(8px); }

.detail-layout { position: relative; }

.infobox-sidebar {
  position: absolute;
  left: calc(100% + 20px);
  top: 0;
  width: 260px;
}
.infobox-sidebar :deep(.wiki-content) { padding: 12px 16px; }

/* 视口不够宽时隐藏悬浮信息框 */
@media (max-width: 1280px) {
  .infobox-sidebar { display: none; }
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

.back-to-top {
  position: fixed;
  bottom: 32px;
  right: 28px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid var(--border);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.75;
  transition: opacity .15s, background .15s;
  z-index: 100;
}
.back-to-top:hover { opacity: 1; background: var(--accent); color: #fff; border-color: var(--accent); }

@media (max-width: 600px) {
  .detail-page { padding: 16px 14px 60px; }
}
</style>
