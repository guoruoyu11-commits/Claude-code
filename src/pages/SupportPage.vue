<template>
  <main class="support-page">
    <nav class="breadcrumb">
      <RouterLink to="/">首页</RouterLink><span>›</span>
      <span>支持与反馈</span>
    </nav>

    <header class="page-head">
      <p class="eyebrow">SUPPORT</p>
      <h1>支持与反馈</h1>
      <p class="lead">
        本站无广告、无付费墙，维护全靠爱发电。<br />
        如果内容对你有帮助，欢迎充电支持；发现问题也欢迎私信反馈。
      </p>
    </header>

    <!-- B 站充电（主推） -->
    <section class="charge-card">
      <div class="charge-deco" aria-hidden="true">⚡</div>
      <div class="charge-body">
        <h2>哔哩哔哩 · 充电</h2>
        <p>
          域名、抓取与翻译的工作量都不小，<b>充电</b>是持续更新最大的动力。<br />
          进入站长 B 站主页点击「充电」按钮即可，任意金额都非常感谢。
        </p>
        <p class="uid-line">站长 UID: <span class="uid">{{ biliUid }}</span></p>
        <a class="charge-btn" :href="spaceLink" target="_blank" rel="noopener noreferrer">
          前往充电 ↗
        </a>
      </div>
    </section>

    <!-- 问题反馈 -->
    <section class="feedback-card">
      <div class="card-title-row">
        <div class="bili-icon" aria-hidden="true">B</div>
        <h2>问题反馈 · B 站私信</h2>
      </div>
      <p class="hint">
        翻译错误、数据过期、排版问题或功能建议，都可以私信站长。
        先复制问题页面链接，粘贴到私信里能最快定位。
      </p>

      <div class="copy-row">
        <input :value="fromUrl" readonly @click="$event.target.select()" aria-label="问题页面链接" />
        <button class="copy-btn" :class="{ done: copied }" @click="copyFromUrl">
          {{ copied ? '已复制 ✓' : '复制链接' }}
        </button>
      </div>
      <p v-if="fromQuery" class="from-note">
        来自：<RouterLink :to="fromQuery">{{ fromQuery }}</RouterLink>
      </p>

      <a class="dm-btn" :href="spaceLink" target="_blank" rel="noopener noreferrer">
        去发私信 ↗
      </a>

      <details class="tips">
        <summary>怎么描述问题最有效？</summary>
        <ul>
          <li><b>哪台机体</b>：页面链接或机体名（如「大地高达 / 朱庇特维形态」）</li>
          <li><b>哪个位置</b>：标题、段落开头几个字，或直接截图</li>
          <li><b>问题类型</b>：翻译不通顺 / 术语译名有误 / 数据过期 / 排版错乱 / 功能建议</li>
          <li><b>期望结果</b>：你觉得应该是什么样的（比如「这个词一般译作 XX」）</li>
        </ul>
      </details>
    </section>
  </main>
</template>

<script setup>
import { computed, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

// ── 站长 B 站 UID（充电与私信共用主页入口）──
const BILI_UID = '599995'
const biliUid = BILI_UID
const spaceLink = `https://space.bilibili.com/${BILI_UID}`

const route = useRoute()

const fromQuery = computed(() => {
  const f = route.query.from
  return typeof f === 'string' && f.startsWith('/') ? f : ''
})
const origin = typeof location !== 'undefined' ? location.origin : ''
const fromUrl = computed(() =>
  fromQuery.value
    ? `${origin}${fromQuery.value}`
    : `${origin || '/'}`
)

const copied = ref(false)
async function copyFromUrl() {
  try {
    await navigator.clipboard.writeText(fromUrl.value)
    copied.value = true
    setTimeout(() => (copied.value = false), 2000)
  } catch {
    const input = document.querySelector('.copy-row input')
    input?.select()
  }
}
</script>

<style scoped>
.support-page {
  max-width: 760px;
  margin: 0 auto;
  padding: 24px 20px 60px;
}

.breadcrumb {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 28px;
  display: flex;
  gap: 8px;
  align-items: center;
}
.breadcrumb a { color: var(--text-muted); text-decoration: none; }
.breadcrumb a:hover { color: var(--accent); }

.page-head h1 {
  font-size: 30px;
  margin: 4px 0 10px;
  letter-spacing: 1px;
}
.eyebrow {
  font-size: 11px;
  letter-spacing: 4px;
  color: var(--accent);
  margin: 0;
}
.lead {
  color: var(--text-muted);
  font-size: 14px;
  line-height: 1.8;
  margin: 0 0 32px;
}

section {
  border-radius: 14px;
  padding: 26px 28px;
  margin-bottom: 20px;
  border: 1px solid var(--border);
  background: var(--bg-card);
}

/* ── 充电卡（主推，粉色大卡） ── */
.charge-card {
  display: grid;
  grid-template-columns: 72px 1fr;
  gap: 20px;
  align-items: start;
  background:
    linear-gradient(135deg, rgba(251, 114, 153, 0.14), rgba(251, 114, 153, 0.04)),
    var(--bg-card);
  border-color: rgba(251, 114, 153, 0.45);
}
.charge-deco {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  background: linear-gradient(135deg, #fb7299, #e35e8b);
  color: #fff;
  font-size: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 24px rgba(251, 114, 153, 0.4);
}
.charge-body h2 {
  font-size: 19px;
  margin: 0 0 8px;
  color: #ffb3c9;
}
.charge-body p {
  margin: 0 0 6px;
  color: var(--text-muted);
  font-size: 13.5px;
  line-height: 1.8;
}
.charge-body b { color: var(--text); }
.uid-line { font-size: 12px; }
.uid { color: var(--text); font-family: monospace; }
.charge-btn {
  display: inline-block;
  margin-top: 10px;
  padding: 11px 26px;
  border-radius: 10px;
  background: linear-gradient(135deg, #fb7299, #e35e8b);
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  text-decoration: none;
  box-shadow: 0 4px 16px rgba(251, 114, 153, 0.35);
  transition: filter 0.15s, transform 0.15s;
}
.charge-btn:hover { filter: brightness(1.08); transform: translateY(-1px); }

/* ── 反馈卡 ── */
.card-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}
.card-title-row h2 { font-size: 17px; margin: 0; }
.bili-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: linear-gradient(135deg, #fb7299, #e35e8b);
  color: #fff;
  font-size: 19px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}
.hint {
  color: var(--text-muted);
  font-size: 13px;
  line-height: 1.7;
  margin: 0 0 14px;
}
.copy-row {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}
.copy-row input {
  flex: 1;
  min-width: 0;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 12px;
  color: var(--text);
  font-size: 13px;
  font-family: monospace;
}
.copy-btn {
  padding: 10px 18px;
  border-radius: 8px;
  border: 1px solid var(--accent);
  background: transparent;
  color: var(--accent);
  font-size: 14px;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s, color 0.15s;
}
.copy-btn:hover { background: var(--accent); color: #fff; }
.copy-btn.done {
  border-color: #3a9040;
  color: #3a9040;
  pointer-events: none;
}
.from-note {
  margin: 0 0 10px;
  font-size: 12px;
  color: var(--text-muted);
}
.from-note a { color: var(--accent); text-decoration: none; }
.dm-btn {
  display: inline-block;
  padding: 9px 20px;
  border-radius: 8px;
  border: 1px solid rgba(251, 114, 153, 0.6);
  color: #fb7299;
  font-size: 13.5px;
  font-weight: 600;
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
}
.dm-btn:hover { background: #fb7299; color: #fff; }

.tips {
  margin-top: 16px;
  border-top: 1px dashed var(--border);
  padding-top: 12px;
  font-size: 13px;
  color: var(--text-muted);
}
.tips summary {
  cursor: pointer;
  color: var(--text-muted);
  font-size: 13px;
  user-select: none;
}
.tips summary:hover { color: var(--accent); }
.tips ul { margin: 10px 0 0; padding-left: 18px; line-height: 2; }
.tips b { color: var(--text); }

@media (max-width: 560px) {
  .charge-card { grid-template-columns: 1fr; justify-items: center; text-align: center; }
  .charge-body p, .charge-body .uid-line { text-align: center; }
  .copy-row { flex-direction: column; }
}
</style>
