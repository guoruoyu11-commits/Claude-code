# イニブ机体排名表 · EXVS2 Infinite Boost Tier List

基于 Vue 3 + Vite 实现的《机动战士高达 EXVS.2 无限强化》（イニブ）机体排名页面，参考 [exvsdb.com](https://exvsdb.com/exvs2ib/rank/) 的排版风格。

---

## 快速开始

```bash
npm install
npm run dev      # → http://localhost:5173
npm run build    # 生产构建 → dist/
npm run preview  # 本地预览构建产物
```

---

## 项目结构

```
Claude-code/
├── index.html                      # Vite HTML 入口
├── package.json
├── vite.config.js
├── Dockerfile                      # 多阶段构建：node → nginx
├── nginx.conf                      # SPA fallback + 缓存头
├── .dockerignore
├── .github/
│   └── workflows/
│       └── deploy.yml              # CI/CD：GitHub Actions → GHCR → ECS
├── public/
│   └── data/
│       └── machines/               # 机体数据 JSON
│           ├── m12504.json         # 原始日文数据（content_nodes）
│           └── m12504_zh.json      # 中文翻译数据 + translation_log
├── scripts/                        # 数据生成脚本（Python，本地运行）
│   ├── scrape_one.py               # 抓取单机体 wiki 页面
│   ├── scrape_scheduler.py         # 批量抓取
│   ├── html_to_nodes.py            # HTML → content_nodes 转换
│   ├── translate_nodes.py          # 节点树翻译（主脚本）
│   ├── translate_scheduler.py      # 批量翻译
│   ├── ja_zh_dict.py               # 固定术语词典
│   └── translate_one.py            # 旧版 HTML 翻译（已弃用）
└── src/
    ├── main.js                     # 创建并挂载 Vue 应用
    ├── App.vue                     # 根组件
    ├── router.js                   # vue-router（history 模式）
    ├── styles/
    │   └── global.css              # 全局 CSS 变量与基础样式
    ├── data/
    │   └── machines.js             # 机体数据源（排名、费用、Tier）
    ├── pages/
    │   ├── HomePage.vue            # / — Tier 排名表 + 费用过滤
    │   └── MachineDetailPage.vue   # /machine/:id — 机体详情 + wiki 内容
    └── components/
        ├── AppHeader.vue           # 顶部导航栏
        ├── CostFilter.vue          # 费用过滤 Tab
        ├── TierTable.vue           # 排名表主体
        ├── TierRow.vue             # 单行 Tier
        ├── MachineCard.vue         # 单个机体卡片（点击跳转详情页）
        └── WikiContent.vue         # 渲染 content_nodes 节点树
```

---

## 功能实现详解

### 1. 全局状态管理：费用筛选

**文件：`src/App.vue`**

整个应用只有一个核心状态：当前选中的费用过滤值 `selectedCost`。所有需要感知筛选的子组件都通过 props 接收过滤后的数据，而不是各自维护状态，做到**单向数据流**。

```js
// App.vue <script setup>
import { ref, computed } from 'vue'
import { MACHINES } from './data/machines.js'

// 唯一状态：当前选中的费用（'all' | '3000' | '2500' | '2000' | '1500'）
const selectedCost = ref('all')

// 派生数据：根据 selectedCost 过滤机体列表
// computed 会在 selectedCost 变化时自动重新计算，Vue 负责缓存
const filteredMachines = computed(() =>
  selectedCost.value === 'all'
    ? MACHINES
    : MACHINES.filter(m => String(m.cost) === selectedCost.value)
)
```

`filteredMachines` 作为 prop 向下传给 `<TierTable>`，后者再按 Tier 分组后传给各 `<TierRow>`。整条数据流：

```
selectedCost (ref)
  ↓ computed
filteredMachines
  ↓ prop
TierTable → byTier (computed)
  ↓ prop
TierRow × 6 → MachineCard × N
```

---

### 2. 费用过滤 Tab：数据驱动动态生成

**文件：`src/components/CostFilter.vue`**

Tab 列表**不是硬编码**的，而是从 `machines.js` 的数据中实时推导，这样只要在数据中新增一个费用档位，Tab 就会自动出现，无需修改组件：

```js
// CostFilter.vue <script setup>
import { computed } from 'vue'
import { MACHINES } from '../data/machines.js'

// 从数据中提取所有不重复的费用，按从大到小排序
const availableCosts = computed(() =>
  [...new Set(MACHINES.map(m => m.cost))].sort((a, b) => b - a)
  // 结果：[3000, 2500, 2000, 1500]
)
```

**组件通信**：该组件通过 `v-model` 与父组件双向绑定，遵循 Vue 3 的 `modelValue` / `update:modelValue` 惯例：

```js
// 接收父组件传入的当前选中值
defineProps({ modelValue: { type: String, default: 'all' } })
// 点击时通知父组件更新
const emit = defineEmits(['update:modelValue'])
// 点击按钮时：emit('update:modelValue', '3000')
```

父组件中只需一行：
```html
<CostFilter v-model="selectedCost" />
```

**激活样式**：每个 Tab 按钮通过 HTML `data-cost` 属性和 CSS 属性选择器实现各自的高亮颜色，避免了用 JS 动态拼接 class：

```css
/* CostFilter.vue <style scoped> */
.cost-tab[data-cost="3000"].active { background: var(--cost-3000); border-color: var(--cost-3000); }
.cost-tab[data-cost="2500"].active { background: var(--cost-2500); border-color: var(--cost-2500); }
/* ... */
```

---

### 3. Tier 分组：一次遍历分桶

**文件：`src/components/TierTable.vue`**

`TierTable` 接收已经被费用过滤过的 `machines` 数组，再按 `tier` 字段分组成字典，供各行使用。分组算法只遍历一次数组（O(n)），而非每行各自 filter 一遍（O(n×6)）：

```js
// TierTable.vue <script setup>
import { computed } from 'vue'
import { TIERS, TIER_META } from '../data/machines.js'

const props = defineProps({ machines: Array })

const byTier = computed(() => {
  // 先为每个 Tier 初始化空数组，保证顺序固定
  const map = {}
  for (const tier of TIERS) map[tier] = []
  // 一次遍历，将每台机体放入对应 Tier 的桶里
  for (const m of props.machines) {
    if (map[m.tier]) map[m.tier].push(m)
  }
  return map
  // 结果示例：{ 'S': [...], 'A+': [...], 'A': [...], 'B+': [...], 'B': [...], 'C': [...] }
})
```

模板中循环 `TIERS` 数组（顺序固定为 `['S','A+','A','B+','B','C']`）渲染行，奇偶行通过 `:class="{ alt: idx % 2 === 1 }"` 交替背景色：

```html
<TierRow
  v-for="(tier, idx) in TIERS"
  :key="tier"
  :meta="TIER_META[tier]"
  :machines="byTier[tier] || []"
  :class="{ alt: idx % 2 === 1 }"
/>
```

Tier 元数据（标签文字、副标签、CSS class 名）集中在 `machines.js` 的 `TIER_META` 常量中，与业务数据放在一起方便维护：

```js
// machines.js
export const TIER_META = {
  'S':  { label: 'S',  sub: '最強', cls: 's'    },
  'A+': { label: 'A+', sub: '',     cls: 'aplus' },
  'A':  { label: 'A',  sub: '',     cls: 'a'     },
  // ...
}
```

---

### 4. 机体卡片：图片加载与渐变兜底

**文件：`src/components/MachineCard.vue`**

卡片的缩略图有两种显示模式，切换逻辑由 `imgFailed` 这个 `ref` 控制：

```js
// MachineCard.vue <script setup>
import { ref } from 'vue'

defineProps({ machine: Object })

// 每个卡片实例独立跟踪自己的图片加载状态
const imgFailed = ref(false)
```

```html
<!-- 只有当 img 字段非空 且 未发生加载错误时，才渲染 <img> 标签 -->
<img
  v-if="machine.img && !imgFailed"
  :src="machine.img"
  :alt="machine.name"
  class="thumb-img"
  @error="imgFailed = true"
/>

<!-- img 为空 或 加载失败时，显示缩写文字（渐变色背景已由父 div 的 CSS class 提供） -->
<span v-if="!machine.img || imgFailed" class="thumb-icon">
  {{ machine.short }}
</span>
```

渐变背景通过动态 class 绑定，根据机体费用自动选择对应颜色：

```html
<div class="machine-thumb" :class="`thumb-${machine.cost}`">
```

```css
/* 四种费用各对应一组渐变 */
.thumb-3000 { background: linear-gradient(135deg, #7b0000, #c62828, #ef5350); }
.thumb-2500 { background: linear-gradient(135deg, #7c3500, #e65100, #ff9800); }
.thumb-2000 { background: linear-gradient(135deg, #003060, #0d47a1, #42a5f5); }
.thumb-1500 { background: linear-gradient(135deg, #1a3d1a, #2e7d32, #66bb6a); }
```

`::before` 伪元素叠加一层高光渐变，模拟卡片光泽感：

```css
.machine-thumb::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,.18) 0%, transparent 55%, rgba(0,0,0,.2) 100%);
  z-index: 1;  /* 叠在背景上，但在文字和图片下方 */
}
```

**z-index 层次**（从下到上）：

| 层 | 元素 | z-index |
|---|---|---|
| 0 | `<img>` 真实图片 | 0 |
| 1 | `::before` 光泽遮罩 | 1 |
| 2 | `.thumb-icon` 缩写文字 | 2 |
| 3 | `.cost-badge` 费用角标 | 3 |

机体名称超过两行时自动截断并显示省略号（通过 `-webkit-line-clamp` 实现），同时在 `title` 属性中保留完整名称供悬停查看：

```css
.machine-name {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
```

---

### 5. 全局主题：CSS 自定义属性

**文件：`src/styles/global.css`**

所有颜色都通过 CSS Custom Properties（变量）定义在 `:root`，各组件的 `<style scoped>` 直接引用变量名，修改主题只需改一处：

```css
:root {
  /* 背景层级 */
  --bg-primary:   #0d1117;   /* 页面底色 */
  --bg-secondary: #161b22;   /* 卡片/面板底色 */
  --bg-card:      #1c2230;   /* 交替行底色 */

  /* 文字 */
  --text-primary: #e6edf3;
  --text-muted:   #8b949e;

  /* 强调色（红色） */
  --accent: #e84040;

  /* 各费用代表色（Tab 激活色 / 图例色 / 费用角标色） */
  --cost-3000: #e53935;
  --cost-2500: #f57c00;
  --cost-2000: #1976d2;
  --cost-1500: #388e3c;
}
```

---

### 6. 响应式布局

机体卡片和 Tier 标签在窄屏（≤ 600px）下缩小尺寸，通过各组件 `<style scoped>` 内的 `@media` 查询实现，互不干扰：

```css
/* MachineCard.vue */
@media (max-width: 600px) {
  .machine-card  { width: 72px; }           /* 90px → 72px */
  .machine-thumb { width: 72px; height: 52px; } /* 66px → 52px */
  .thumb-icon    { font-size: 13px; }       /* 17px → 13px */
  .machine-name  { font-size: 9px; }        /* 10px → 9px  */
}

/* TierRow.vue */
@media (max-width: 600px) {
  .tier-label { min-width: 44px; width: 44px; font-size: 20px; }
}
```

---

### 7. 数据源结构

**文件：`src/data/machines.js`**

数据与视图完全分离，修改排名只需编辑 `machines.js`，无需触碰任何组件：

```js
export const MACHINES = [
  {
    id:    'nu-gundam',   // 唯一 key（供 v-for :key 使用）
    name:  'νガンダム',   // 日文全名（卡片下方文字）
    short: 'νG',          // 缩写（无图时卡片中央显示）
    cost:  3000,          // 费用档位：3000 / 2500 / 2000 / 1500
    tier:  'S',           // Tier：'S' | 'A+' | 'A' | 'B+' | 'B' | 'C'
    img:   '',            // 图片 URL（空则显示渐变兜底）
  },
  // ...
]

// Tier 渲染顺序（固定，不受数据顺序影响）
export const TIERS = ['S', 'A+', 'A', 'B+', 'B', 'C']

// Tier 显示元数据（标签、副标签、CSS class）
export const TIER_META = {
  'S':  { label: 'S',  sub: '最強',  cls: 's'    },
  'A+': { label: 'A+', sub: '',      cls: 'aplus' },
  'A':  { label: 'A',  sub: '',      cls: 'a'     },
  'B+': { label: 'B+', sub: '',      cls: 'bplus' },
  'B':  { label: 'B',  sub: '',      cls: 'b'     },
  'C':  { label: 'C',  sub: '要強化', cls: 'c'    },
}
```

---

## 数据生成流程

机体 JSON 数据通过本地 Python 脚本生成，commit 后随构建打入镜像：

```
py scripts/scrape_one.py <id>        # 抓取 wiki → public/data/machines/<id>.json
py scripts/translate_nodes.py <id>   # 翻译 → public/data/machines/<id>_zh.json

# 批量操作
py scripts/scrape_scheduler.py       # 批量抓取（跳过已有）
py scripts/translate_scheduler.py    # 批量翻译（跳过已有）
```

翻译脚本先匹配词典（~95 条固定术语，无 API 消耗），剩余内容分批发给 Gemini。支持断点续传（`{id}_zh_nodes_progress.json`）。翻译结果包含 `translation_log`，记录每个分段的原文、译文和翻译方式（`dict` / `gemini`）。

Python 依赖：`pip install beautifulsoup4 playwright google-genai`，首次运行 `py -m playwright install chromium`。根目录需 `.env` 文件，内含 `GEMINI_API_KEY=<your_key>`。

---

## 部署

生产环境使用 Docker 容器运行在阿里云 ECS，nginx 监听 80 端口。

### CI/CD 流程

push 到 `main` 分支自动触发：

```
git push origin main
    ↓
GitHub Actions:
  1. npm ci && npm run build
  2. docker build → push 到 GHCR (ghcr.io/<owner>/<repo>:latest)
  3. SSH 到 ECS → docker pull → 重启容器
```

### 一次性配置

1. **ECS 安装 Docker**：`curl -fsSL https://get.docker.com | sh && systemctl enable --now docker`
2. **开放安全组** TCP 80 端口（入方向）
3. **创建 GitHub PAT**（Settings → Developer settings → Tokens，勾选 `read:packages`）
4. **在 GitHub 仓库添加 Secrets**（Settings → Secrets and variables → Actions）：

| Secret | 说明 |
|--------|------|
| `GH_PAT` | GitHub PAT（`read:packages`），ECS 拉取镜像用 |
| `ECS_HOST` | ECS 公网 IP |
| `ECS_USERNAME` | SSH 用户名（通常 `root`） |
| `ECS_SSH_KEY` | SSH 私钥内容（`cat ~/.ssh/id_ed25519`） |

---

## 添加机体图片

1. 浏览器打开 [https://exvsdb.com/exvs2ib/rank/](https://exvsdb.com/exvs2ib/rank/)
2. `F12` → Network 面板 → 过滤图片请求 → 复制目标图片的完整 URL
3. 填入 `src/data/machines.js` 对应机体的 `img` 字段：

```js
// 修改前
{ id: 'nu-gundam', ..., img: '' },

// 修改后
{ id: 'nu-gundam', ..., img: 'https://exvsdb.com/exvs2ib/images/nu_gundam.webp' },
```

`img` 为空或加载失败时，自动回退到费用色渐变，无需额外处理。

---

## 免责声明

- 本项目为非官方爱好者项目，与万代南梦宫娱乐株式会社无任何关联
- 机体排名仅供参考，不代表官方立场
- © 機動戦士ガンダム EXVS.2 インフィニットブースト ™ & © BANDAI NAMCO Entertainment Inc.
