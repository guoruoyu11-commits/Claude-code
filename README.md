# EXVS2IB 机体图鉴

《机动战士高达 EXVS.2 无限强化》（イニブ）机体中文图鉴，提供 Tier 排名表与机体详情的中文翻译。

网站：**[exvsdb-cn.top](https://exvsdb-cn.top)**

---

## 功能

- **Tier 排名表**：按费用筛选（3000 / 2500 / 2000 / 1500），点击机体卡片进入详情页
- **机体详情**：翻译自日文 wiki（[atwiki](https://w.atwiki.jp/exvs2infiniteboost/)），含数据表格、技能说明、攻略等
- **中日切换**：有中文译文的机体支持中日文内容切换
- **子页面支持**：多形态机体（如独角兽、奥德赛斯）各子页面独立展示

---

## 技术栈

- **前端**：Vue 3 + Vite + vue-router（history 模式）
- **部署**：Docker + nginx，托管于阿里云 ECS，HTTPS
- **CI/CD**：GitHub Actions → GHCR → SSH 自动部署
- **翻译**：Python 脚本 + Gemini API，支持多进程批量处理

---

## 本地开发

```bash
npm install
npm run dev      # → http://localhost:5173
npm run build    # 生产构建 → dist/
```

---

## 数据生成

机体数据通过本地 Python 脚本从日文 wiki 抓取并翻译，提交后随 Docker 构建打入镜像。

**依赖安装：**
```bash
pip install beautifulsoup4 playwright google-genai
py -m playwright install chromium
```

根目录创建 `.env`，内含：
```
GEMINI_API_KEY=<your_key>
```

**常用命令：**
```bash
# 单机体完整流程（抓取 → 翻译 → 本地化图片）
py scripts/pipeline.py m12504

# 多机体并行（10 线程）
py scripts/pipeline.py m12504 m14801 m24501 --workers 10

# 仅翻译（跳过抓取）
py scripts/pipeline.py m12504 --skip-scrape

# 强制重新处理
py scripts/pipeline.py m12504 --force
```

---

## 项目结构

```
├── src/
│   ├── data/machines.js          # 机体数据源（排名、费用、Tier）
│   ├── pages/
│   │   ├── HomePage.vue          # Tier 排名表 + 费用过滤
│   │   └── MachineDetailPage.vue # 机体详情页
│   └── components/
│       ├── WikiContent.vue       # content_nodes 节点树渲染器
│       ├── TierTable.vue / TierRow.vue / MachineCard.vue
│       └── CostFilter.vue / AppHeader.vue
├── public/
│   ├── data/machines/            # 机体 JSON（日文原文 + 中文译文）
│   └── images/                  # 机体图片（本地化缓存）
├── scripts/                      # Python 数据生成脚本
│   ├── pipeline.py               # 主流程入口（抓取+翻译+图片）
│   ├── scrape_one.py             # 单机体 wiki 抓取
│   ├── translate_nodes.py        # 节点树翻译（Gemini）
│   ├── ja_zh_dict.py             # 固定术语词典
│   ├── download_assets.py        # 下载机体图片
│   └── localize_wiki_images.py   # 替换 wiki 图片为本地路径
├── Dockerfile                    # 多阶段构建（node → nginx）
├── nginx.conf                    # HTTPS + SPA fallback + 缓存头
└── .github/workflows/deploy.yml  # CI/CD 自动部署
```

---

## 部署

### CI/CD 自动部署

push 到 `main` 分支自动触发：构建前端 → 打 Docker 镜像 → 推送到 GHCR → SSH 到 ECS 拉取并重启容器。

**所需 GitHub Secrets：**

| Secret | 说明 |
|--------|------|
| `GH_PAT` | GitHub PAT（`read:packages`），ECS 拉取镜像用 |
| `ECS_HOST` | ECS 公网 IP |
| `ECS_USERNAME` | SSH 用户名 |
| `ECS_SSH_KEY` | SSH 私钥内容 |

### HTTPS 证书

在 ECS 上将证书文件放置于 `/etc/ssl/exvsdb/`：
```
/etc/ssl/exvsdb/exvsdb-cn.top.pem
/etc/ssl/exvsdb/exvsdb-cn.top.key
```
容器通过 Docker volume 只读挂载，nginx 自动加载。

### 本地 Docker 测试

```bash
docker build -t exvsdb .
docker run -p 80:80 -p 443:443 exvsdb
```

---

## 免责声明

本项目为非官方爱好者项目，与万代南梦宫娱乐株式会社无任何关联。机体排名仅供参考，不代表官方立场。

© 機動戦士ガンダム EXVS.2 インフィニットブースト ™ & © BANDAI NAMCO Entertainment Inc.
