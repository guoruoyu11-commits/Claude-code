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
        <div v-if="loading" class="status-box">加载中…</div>
        <WikiContent v-else-if="pageData"
          :nodes="pageData.content_nodes ?? null"
          :html="pageData.content_nodes ? null : pageData.content_html"
          :sub-pages="subPages"
          :parent-url="machine.link"
          :machine-id="id"
          @select-sub="selectSub"
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

  <button v-show="showTop" class="back-to-top" @click="scrollToTop" aria-label="返回顶部">↑</button>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { MACHINES } from '../data/machines.js'
import WikiContent from '../components/WikiContent.vue'

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

async function loadPageData(machineId) {
  loading.value = true
  pageData.value = null
  currentSub.value = null
  subPages.value = []
  try {
    const zhRes = await fetch(`/data/machines/${machineId}_zh.json`)
    hasZh.value = zhRes.ok
    if (!hasZh.value) lang.value = 'ja'

    let data
    if (lang.value === 'zh' && hasZh.value) {
      data = await zhRes.json()
    } else {
      const res = await fetch(`/data/machines/${machineId}.json`)
      if (res.ok) data = await res.json()
    }
    if (data) {
      pageData.value = data
      subPages.value = data.sub_pages || []
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
    const zhFile = `/data/machines/${fileId}_zh.json`
    const zhRes = await fetch(zhFile)
    const url = lang.value === 'zh' && zhRes.ok ? zhFile : `/data/machines/${fileId}.json`
    const res = await fetch(url)
    if (res.ok) pageData.value = await res.json()
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
    await loadPageData(id.value)
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
  margin-bottom: 32px;
  font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-size: 15px;
  line-height: 1.9;
  letter-spacing: 0.02em;
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
