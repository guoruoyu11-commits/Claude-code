<template>
  <main class="feedback-page">
    <nav class="breadcrumb">
      <RouterLink to="/">首页</RouterLink><span>›</span>
      <span>问题反馈</span>
    </nav>

    <header class="page-head">
      <p class="eyebrow">FEEDBACK</p>
      <h1>问题反馈</h1>
      <p class="lead">
        发现翻译错误、数据过期、页面排版问题，或者有想要的功能？<br />
        通过 B 站私信联系站长即可，附上问题页面链接能最快定位。
      </p>
    </header>

    <!-- B 站私信卡片 -->
    <section class="channel-card">
      <div class="bili-icon" aria-hidden="true">B</div>
      <div class="channel-info">
        <h2>B 站私信 <span class="tag">推荐</span></h2>
        <p>
          跳转站长 B 站主页，点击「发消息」即可私信。<br />
          <span v-if="biliUid" class="uid">UID: {{ biliUid }}</span>
        </p>
      </div>
      <a
        class="bili-btn"
        :class="{ disabled: !biliLink }"
        :href="biliLink || undefined"
        :aria-disabled="!biliLink"
        target="_blank"
        rel="noopener noreferrer"
      >前往 B 站主页 ↗</a>
    </section>

    <!-- 复制问题页面链接 -->
    <section class="copy-card">
      <h2>附上问题页面链接</h2>
      <p class="hint">点击复制后粘贴到私信里，站长就能直接定位到出问题的机体页。</p>
      <div class="copy-row">
        <input :value="fromUrl" readonly @click="$event.target.select()" aria-label="问题页面链接" />
        <button class="copy-btn" :class="{ done: copied }" @click="copyFromUrl">
          {{ copied ? '已复制 ✓' : '复制链接' }}
        </button>
      </div>
      <p v-if="fromQuery" class="from-note">
        来自：<RouterLink :to="fromQuery">{{ fromQuery }}</RouterLink>
      </p>
    </section>

    <!-- 反馈内容建议 -->
    <section class="tips-card">
      <h2>怎么描述问题最有效</h2>
      <ul>
        <li><b>哪台机体</b>：页面链接或机体名（如「大地高达 / 朱庇特维形态」）</li>
        <li><b>哪个位置</b>：标题、段落开头几个字，或直接截图</li>
        <li><b>问题类型</b>：翻译不通顺 / 术语译名有误 / 数据过期 / 排版错乱 / 功能建议</li>
        <li><b>期望结果</b>：你觉得应该是什么样的（比如「这个词一般译作 XX」）</li>
      </ul>
    </section>
  </main>
</template>

<script setup>
import { computed, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

// ── 站长 B 站 UID（配置处：填入数字 UID 即生效，卡片与按钮自动启用）──
const BILI_UID = '599995'

const route = useRoute()
const biliUid = BILI_UID && !Number.isNaN(Number(BILI_UID)) ? BILI_UID : ''
const biliLink = biliUid ? `https://space.bilibili.com/${biliUid}` : ''

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
    // 剪贴板 API 不可用时退回选中文本，让用户手动复制
    const input = document.querySelector('.copy-row input')
    input?.select()
  }
}
</script>

<style scoped>
.feedback-page {
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
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 22px 24px;
  margin-bottom: 18px;
}
section h2 {
  font-size: 16px;
  margin: 0 0 8px;
}

/* B 站卡片 */
.channel-card {
  display: grid;
  grid-template-columns: 52px 1fr auto;
  gap: 16px;
  align-items: center;
}
.bili-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  background: linear-gradient(135deg, #fb7299, #e35e8b);
  color: #fff;
  font-size: 26px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 18px rgba(251, 114, 153, 0.3);
}
.channel-info p {
  margin: 0;
  color: var(--text-muted);
  font-size: 13px;
  line-height: 1.7;
}
.tag {
  font-size: 10px;
  color: #fb7299;
  border: 1px solid rgba(251, 114, 153, 0.5);
  border-radius: 4px;
  padding: 1px 6px;
  margin-left: 6px;
  vertical-align: 2px;
}
.uid { color: var(--text); font-family: monospace; }
.bili-btn {
  display: inline-block;
  padding: 10px 18px;
  border-radius: 8px;
  background: #fb7299;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  white-space: nowrap;
  transition: filter 0.15s;
}
.bili-btn:hover { filter: brightness(1.1); }
.bili-btn.disabled {
  background: var(--border);
  color: var(--text-muted);
  pointer-events: none;
}

/* 复制链接卡片 */
.hint {
  color: var(--text-muted);
  font-size: 13px;
  margin: 0 0 12px;
}
.copy-row {
  display: flex;
  gap: 10px;
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
  margin: 10px 0 0;
  font-size: 12px;
  color: var(--text-muted);
}
.from-note a { color: var(--accent); text-decoration: none; }

/* 建议卡片 */
.tips-card ul {
  margin: 0;
  padding-left: 18px;
  color: var(--text-muted);
  font-size: 13px;
  line-height: 2;
}
.tips-card b { color: var(--text); }

@media (max-width: 560px) {
  .channel-card {
    grid-template-columns: 1fr;
    text-align: center;
    justify-items: center;
  }
  .copy-row { flex-direction: column; }
}
</style>
