# イニブ机体排名表 · EXVS2 Infinite Boost Tier List

基于 Vue 3 + Vite 实现的《机动战士高达 EXVS.2 无限强化》（イニブ）机体排名页面，参考 [exvsdb.com](https://exvsdb.com/exvs2ib/rank/) 的排版风格。

---

## 功能特性

- **Tier 分级展示**：S / A+ / A / B+ / B / C 六档，对应最强到待强化
- **费用过滤**：点击 Tab 可按 3000 / 2500 / 2000 / 1500 费用筛选机体
- **动态 Tab**：过滤 Tab 由数据自动生成，数据中存在哪些费用就显示哪些
- **机体卡片**：支持显示原网页图片链接；图片未配置或加载失败时自动回退为费用色渐变占位图
- **暗色主题**：仿 EXVS 风格深色配色，响应式布局，兼容手机端

---

## 技术栈

| 技术 | 版本 |
|------|------|
| Vue | 3.4+ |
| Vite | 5.x |
| @vitejs/plugin-vue | 5.x |

---

## 项目结构

```
Claude-code/
├── index.html                  # Vite HTML 入口
├── package.json
├── vite.config.js
└── src/
    ├── main.js                 # 创建并挂载 Vue 应用
    ├── App.vue                 # 根组件，管理费用筛选状态
    ├── styles/
    │   └── global.css          # 全局 CSS 变量与基础样式
    ├── data/
    │   └── machines.js         # 机体数据（名称、费用、Tier、图片 URL）
    └── components/
        ├── AppHeader.vue       # 顶部导航栏
        ├── CostFilter.vue      # 费用过滤 Tab 组件
        ├── TierTable.vue       # 排名表主体（含图例与计数）
        ├── TierRow.vue         # 单行 Tier（标签 + 机体卡片列表）
        └── MachineCard.vue     # 单个机体卡片（图片 + 名称 + 费用标签）
```

---

## 快速开始

**前提条件**：Node.js 18+

```bash
# 克隆项目
git clone https://github.com/guoruoyu11-commits/Claude-code.git
cd Claude-code

# 安装依赖
npm install

# 启动开发服务器
npm run dev
# → 访问 http://localhost:5173

# 生产构建
npm run build

# 本地预览构建产物
npm run preview
```

---

## 添加机体图片

机体图片 URL 统一存放在 `src/data/machines.js`，每条记录的 `img` 字段默认为空字符串。

**步骤：**

1. 用浏览器打开 [https://exvsdb.com/exvs2ib/rank/](https://exvsdb.com/exvs2ib/rank/)
2. 按 `F12` 打开开发者工具 → Network 面板 → 筛选图片请求
3. 复制对应机体的完整图片 URL
4. 填入 `src/data/machines.js` 中对应机体的 `img` 字段：

```js
// 修改前
{ id: 'nu-gundam', name: 'νガンダム', short: 'νG', cost: 3000, tier: 'S', img: '' },

// 修改后
{ id: 'nu-gundam', name: 'νガンダム', short: 'νG', cost: 3000, tier: 'S', img: 'https://exvsdb.com/exvs2ib/images/nu_gundam.webp' },
```

`img` 为空或图片加载失败时，卡片会自动显示费用色渐变作为兜底。

---

## 数据说明

`src/data/machines.js` 中每条机体数据格式如下：

```js
{
  id:    'strike-freedom',          // 唯一标识符（英文，用于 key）
  name:  'ストライクフリーダムガンダム', // 日文全名（显示在卡片下方）
  short: 'SF',                      // 缩写（无图时显示在卡片中央）
  cost:  3000,                      // 费用：3000 / 2500 / 2000 / 1500
  tier:  'S',                       // Tier：'S' | 'A+' | 'A' | 'B+' | 'B' | 'C'
  img:   '',                        // 机体图片 URL（留空则使用渐变占位）
}
```

---

## 免责声明

- 本项目为非官方爱好者项目，与万代南梦宫娱乐株式会社无任何关联
- 机体排名仅供参考，基于公开对战数据整理，不代表官方立场
- © 机動戦士ガンダム EXVS.2 インフィニットブースト ™ & © BANDAI NAMCO Entertainment Inc.
