# 抓取单个机体的攻略页面并保存为 JSON。
#
# 作为模块使用：
#   from scrape_one import scrape_one
#   result = scrape_one("m12504")
#
# 作为命令行使用：
#   py scrape_one.py m12504
#   py scrape_one.py m12504 --force
#   py scrape_one.py m12504 --debug

import re
import sys
import json
import time
import argparse
from datetime import datetime, timezone
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("缺少依赖，请先运行：pip install beautifulsoup4")
    sys.exit(1)

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    _PLAYWRIGHT_OK = True
except ImportError:
    _PLAYWRIGHT_OK = False

# ─── 路径 ────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent.parent
MACHINES_JS = BASE_DIR / "src" / "data" / "machines.js"
OUTPUT_DIR  = BASE_DIR / "public" / "data" / "machines"

# ─── HTTP ────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "ja-JP,ja;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}

# 模块级 Playwright 浏览器实例，批量抓取时复用（避免重复启动）
_pw_context = None
_pw_instance = None


def get_browser_context():
    """获取（或创建）持久 Playwright 浏览器上下文。"""
    global _pw_context, _pw_instance
    if _pw_context is not None:
        return _pw_context

    if not _PLAYWRIGHT_OK:
        print("[ERR] Playwright 未安装，请运行：pip install playwright && py -m playwright install chromium")
        sys.exit(1)

    _pw_instance = sync_playwright().start()
    browser = _pw_instance.chromium.launch(headless=True)
    _pw_context = browser.new_context(
        user_agent=HEADERS["User-Agent"],
        locale="ja-JP",
        extra_http_headers={
            "Accept-Language": HEADERS["Accept-Language"],
        },
    )
    return _pw_context


def close_browser():
    """关闭浏览器，释放资源。批量任务结束后调用。"""
    global _pw_context, _pw_instance
    if _pw_context:
        _pw_context.close()
        _pw_context = None
    if _pw_instance:
        _pw_instance.stop()
        _pw_instance = None

# ─── 工具函数 ─────────────────────────────────────────────────

def load_machines() -> dict[str, dict]:
    """从 machines.js 读取所有机体，返回 {id: {id, name, link}} 字典。"""
    content = MACHINES_JS.read_text(encoding="utf-8")
    pattern = re.compile(
        r"\{\s*id:\s*'(m\d+)'.*?name:\s*'([^']*)'.*?link:\s*'([^']*)'\s*\}",
        re.DOTALL,
    )
    result = {}
    for m in pattern.finditer(content):
        mid, name, link = m.group(1), m.group(2), m.group(3)
        result[mid] = {"id": mid, "name": name, "link": link}
    return result


def fetch_html(url: str, retries: int = 3) -> str | None:
    """用 Playwright 真实浏览器加载页面，展开折叠内容后返回 HTML。"""
    ctx = get_browser_context()

    for attempt in range(retries):
        page = ctx.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            try:
                page.wait_for_selector("#wikibody", timeout=10000)
            except PWTimeout:
                pass

            # 展开所有 plugin-openclose 折叠块（目次等默认折叠的内容）
            page.evaluate("""
                document.querySelectorAll('.plugin-openclose-contents').forEach(el => {
                    el.style.display = 'block';
                });
            """)
            # 等待目次内容注入（JS 动态生成）
            try:
                page.wait_for_selector(".plugin_contents", timeout=5000)
            except PWTimeout:
                pass

            html = page.content()
            return html
        except Exception as e:
            if attempt == retries - 1:
                print(f"  [FAIL] 页面加载失败: {e}")
                return None
            wait = 2 ** attempt
            print(f"  [RETRY] 等待 {wait}s 后重试 ({attempt + 1}/{retries - 1})...")
            time.sleep(wait)
        finally:
            page.close()
    return None


CONTENT_SELECTORS = [
    "#wikibody",
    ".wikibody",
    "#content_block",
    "#content",
    ".content",
    "#main",
    "article",
]


def extract_content(soup: BeautifulSoup) -> tuple[str, str]:
    """从 BeautifulSoup 中提取页面标题和正文 HTML。"""
    title = soup.title.get_text(strip=True) if soup.title else ""

    content_tag = None
    for sel in CONTENT_SELECTORS:
        content_tag = soup.select_one(sel)
        if content_tag:
            break

    if not content_tag:
        divs = soup.find_all("div")
        content_tag = max(divs, key=lambda d: len(d.get_text())) if divs else soup.body

    if not content_tag:
        return title, "<p>内容提取失败</p>"

    for tag in content_tag.find_all(["script", "style", "iframe", "ins", "noscript"]):
        tag.decompose()
    # atwiki 特有的无用元素：编辑按钮、いいね、标签、最終更新、广告
    remove_classes = re.compile(r"edit|toolbar|sidebar|atwiki-like|atwiki-page-tags|atwiki-page-keyword|atwiki-lastmodify|atwiki-ads|atwiki_autoads", re.I)
    for tag in content_tag.find_all(class_=remove_classes):
        tag.decompose()
    for tag in content_tag.find_all(id=re.compile(r"atwiki-page-tags|like|sns|^gpt-", re.I)):
        tag.decompose()
    for tag in content_tag.find_all("form"):
        tag.decompose()
    # 找到「コメント欄」标题，删除它及其后所有兄弟节点（评论列表）
    COMMENT_PATTERN = re.compile(r"コメント|評価|掲示板", re.I)
    for heading in content_tag.find_all(["h2", "h3", "h4"]):
        if COMMENT_PATTERN.search(heading.get_text()):
            for sibling in list(heading.find_next_siblings()):
                sibling.decompose()
            heading.decompose()
            break

    # 同时清理目次中残留的评论区条目
    for toc in content_tag.find_all(class_="plugin_contents"):
        for li in toc.find_all("li"):
            if COMMENT_PATTERN.search(li.get_text()):
                li.decompose()

    return title, str(content_tag)


def debug_print_structure(soup: BeautifulSoup, url: str):
    """打印页面 HTML 骨架，用于调试选择器。"""
    print(f"\n{'=' * 60}")
    print(f"URL: {url}")
    print(f"{'=' * 60}")

    print("\n[body 直接子元素]")
    for tag in (soup.body.children if soup.body else []):
        if hasattr(tag, "name") and tag.name:
            cls = " ".join(tag.get("class", []))
            tid = tag.get("id", "")
            print(f"  <{tag.name} id='{tid}' class='{cls}'>")

    print("\n[所有 id 属性]")
    for tag in soup.find_all(id=True):
        print(f"  #{tag['id']} <{tag.name}>")

    print("\n[h1~h4 标题]")
    for tag in soup.find_all(["h1", "h2", "h3", "h4"]):
        print(f"  <{tag.name}> {tag.get_text(strip=True)[:80]}")


# ─── 子页面检测 ───────────────────────────────────────────────

def extract_sub_pages(soup: BeautifulSoup, current_url: str) -> list[dict]:
    """
    检测顶部子页面导航（如 综合解说 / 地球三型 / 木星五型）。
    返回不含当前页面的子页面列表：[{name, url, page_num}]
    """
    content_tag = soup.select_one("#wikibody") or soup.body
    if not content_tag:
        return []

    cur_match = re.search(r"/pages/(\d+)\.html", current_url)
    cur_num = cur_match.group(1) if cur_match else None

    sub_pages = []
    for span in content_tag.find_all("span", style=re.compile(r"font-size\s*:\s*medium", re.I)):
        bold = span.find("span", style=re.compile(r"font-weight\s*:\s*bold", re.I))
        links = span.find_all("a", href=re.compile(r"/pages/\d+\.html"))
        if not bold or not links:
            continue
        for link in links:
            href = link.get("href", "")
            m = re.search(r"/pages/(\d+)\.html", href)
            if not m or m.group(1) == cur_num:
                continue
            full_url = "https:" + href if href.startswith("//") else href
            sub_pages.append({"name": link.get_text(strip=True), "url": full_url, "page_num": m.group(1)})
        break  # 只处理第一个匹配的导航 span
    return sub_pages


def scrape_sub_page(machine_id: str, page_num: str, name: str, url: str, force: bool = False) -> dict | None:
    """抓取并保存一个子页面，返回保存结果或 None。"""
    sub_id = f"{machine_id}_p{page_num}"
    out_path = OUTPUT_DIR / f"{sub_id}.json"
    if not force and out_path.exists():
        return {"status": "skipped", "file": sub_id}

    html = fetch_html(url)
    if html is None:
        return None
    soup = BeautifulSoup(html, "html.parser")
    _, content_html = extract_content(soup)
    data = {
        "status": "ok",
        "id": sub_id,
        "name": name,
        "parent_id": machine_id,
        "url": url,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "content_html": content_html,
    }
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


# ─── 核心函数 ─────────────────────────────────────────────────

def scrape_one(machine_id: str, force: bool = False, debug: bool = False) -> dict | None:
    """
    抓取并保存单个机体页面。

    返回值：
      {"status": "skipped"}  — 文件已存在且 force=False
      {"status": "ok", ...}  — 成功保存，包含完整数据
      None                   — 抓取或解析失败
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"{machine_id}.json"

    if not force and not debug and out_path.exists():
        return {"status": "skipped"}

    machines = load_machines()
    machine = machines.get(machine_id)
    if not machine:
        print(f"[ERR] machines.js 中未找到机体 ID: {machine_id}")
        return None
    if not machine["link"]:
        print(f"[ERR] 机体 {machine_id} 没有 link 字段")
        return None

    html = fetch_html(machine["link"])
    if html is None:
        return None

    soup = BeautifulSoup(html, "html.parser")

    if debug:
        debug_print_structure(soup, machine["link"])
        return {"status": "debug"}

    title, content_html = extract_content(soup)

    # 检测子页面导航并抓取
    sub_pages_info = extract_sub_pages(soup, machine["link"])
    sub_pages_saved = []
    for sp in sub_pages_info:
        print(f"  >> 子页面: {sp['name']} ({sp['url']})")
        result = scrape_sub_page(machine_id, sp["page_num"], sp["name"], sp["url"], force=force)
        if result is None:
            print(f"  [WARN] 子页面抓取失败: {sp['url']}")
        elif result.get("status") == "skipped":
            print(f"  -- 子页面已存在，跳过: {result['file']}")
            sub_pages_saved.append({"name": sp["name"], "file": result["file"], "url": sp["url"]})
        else:
            print(f"  [OK] 子页面已保存: {result['id']}.json")
            sub_pages_saved.append({"name": sp["name"], "file": result["id"], "url": sp["url"]})

    data = {
        "status": "ok",
        "id": machine_id,
        "name": machine["name"],
        "title": title,
        "url": machine["link"],
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "content_html": content_html,
    }
    if sub_pages_saved:
        data["sub_pages"] = sub_pages_saved

    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


# ─── CLI ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="抓取单个机体攻略页面")
    parser.add_argument("id",      type=str,            help="机体 ID，如 m12504")
    parser.add_argument("--force", action="store_true", help="强制重新抓取（覆盖已有文件）")
    parser.add_argument("--debug", action="store_true", help="打印 HTML 骨架，不写文件")
    args = parser.parse_args()

    print(f">> 处理 {args.id}")
    result = scrape_one(args.id, force=args.force, debug=args.debug)

    if result is None:
        print("[FAIL] 抓取失败")
        sys.exit(1)
    elif result.get("status") == "skipped":
        print("-- 已存在，跳过（使用 --force 强制重新抓取）")
    elif result.get("status") == "debug":
        print("\n[调试模式] 未写入文件")
    else:
        print(f"[OK] 已保存至 {OUTPUT_DIR / (args.id + '.json')}")


if __name__ == "__main__":
    main()
