# 更新 src/data/machines.js：以 exvsdb.com 最新榜单为准，保留本地中文名 / atwiki link / 本地图片路径。
#
# 相比根目录 generate_machines.py 的改进：
#   - 不丢失 link 字段（抓取详情页必需）与本地 img 路径
#   - 已有机体沿用本地中文译名，仅更新 cost/tier 与组内排序
#   - 新机体从 NEW_MACHINES 字典补充中文名与 atwiki 链接
#
# 用法：
#   python3 scripts/update_machines.py               # 抓取线上榜单并合并（缓存 10 分钟）
#   python3 scripts/update_machines.py --dry-run     # 只打印变更，不写文件

import re
import sys
import argparse
import urllib.request
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR   = Path(__file__).parent.parent
MACHINES_JS = BASE_DIR / "src" / "data" / "machines.js"
RANK_URL   = "https://exvsdb.com/exvs2ib/rank/"
RANK_CACHE = BASE_DIR / ".rank_cache.html"

# ─── 新机体元数据（线上出现但本地缺失时从这里补充）───────────────
# name: 中文译名；ja: 日文原名（用于生成 short）；link: atwiki 攻略页
NEW_MACHINES = {
    "13104": {"name": "黑骑士斯科德·卡尔拉", "ja": "ブラックナイトスコード カルラ",
              "link": "https://w.atwiki.jp/exvs2infiniteboost/pages/772.html"},
    "20405": {"name": "里·加济(阿姆罗搭乘)", "ja": "リ・ガズィ(アムロ搭乗)",
              "link": "https://w.atwiki.jp/exvs2infiniteboost/pages/783.html"},
    "22606": {"name": "高达阿修塔隆·寄居蟹", "ja": "ガンダムアシュタロン・ハーミットクラブ",
              "link": "https://w.atwiki.jp/exvs2infiniteboost/pages/771.html"},
    "24502": {"name": "沃多姆舱体＋", "ja": "ウォドムポッド+",
              "link": "https://w.atwiki.jp/exvs2infiniteboost/pages/707.html"},
    "24706": {"name": "∫极限高达", "ja": "∫エクストリームガンダム",
              "link": "https://w.atwiki.jp/exvs2infiniteboost/pages/754.html"},
    "32309": {"name": "玫瑰高达", "ja": "ガンダムローズ",
              "link": "https://w.atwiki.jp/exvs2infiniteboost/pages/735.html"},
}

# ─── 抓取线上榜单 ──────────────────────────────────────────────

TIER_MAP = {"S": "S", "Ap": "A+", "A": "A", "Am": "A-",
            "Bp": "B+", "B": "B", "Bm": "B-", "C": "C", "Z": "Z"}

def fetch_rank_html() -> str:
    import time
    if RANK_CACHE.exists() and time.time() - RANK_CACHE.stat().st_mtime < 600:
        print("  [cache] 使用 10 分钟内的榜单缓存")
        return RANK_CACHE.read_text(encoding="utf-8")
    req = urllib.request.Request(RANK_URL, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://exvsdb.com/",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    RANK_CACHE.write_text(html, encoding="utf-8")
    print(f"  [ok] 榜单已抓取并缓存 ({len(html)} bytes)")
    return html

def parse_online(html: str) -> dict[str, dict]:
    """解析线上榜单，返回 {id_num: {ja, cost, tier}}，同组内保持线上顺序。"""
    online: dict[str, dict] = {}
    pattern = re.compile(r'<td id="cost(\d+)List(\w+)">(.*?)(?=</td></tr>)', re.DOTALL)
    img_pattern = re.compile(
        r'<img src="https://exvsdb\.com/wp-content/images/exvs2ib/(\d+)\.png"[^>]*alt="([^"]+)"')
    for m in pattern.finditer(html):
        cost, tier = int(m.group(1)), TIER_MAP.get(m.group(2), m.group(2))
        for im in img_pattern.finditer(m.group(3)):
            online[im.group(1)] = {"ja": im.group(2), "cost": cost, "tier": tier}
    return online

# ─── 解析本地 machines.js ──────────────────────────────────────

LOCAL_LINE = re.compile(
    r"\{\s*id:\s*'m(\d+)'\s*,\s*name:\s*'((?:[^'\\]|\\.)*)'\s*,\s*short:\s*'((?:[^'\\]|\\.)*)'"
    r"\s*,\s*cost:\s*(\d+)\s*,\s*tier:\s*'([^']*)'\s*,\s*img:\s*'([^']*)'"
    r"\s*,\s*link:\s*'([^']*)'\s*,?\s*\}",
    re.DOTALL)

def parse_local() -> dict[str, dict]:
    local: dict[str, dict] = {}
    for m in LOCAL_LINE.finditer(MACHINES_JS.read_text(encoding="utf-8")):
        local[m.group(1)] = {
            "id": m.group(1), "name": m.group(2), "short": m.group(3),
            "cost": int(m.group(4)), "tier": m.group(5), "img": m.group(6), "link": m.group(7),
        }
    return local

# ─── 生成 machines.js ──────────────────────────────────────────

def make_short(ja: str) -> str:
    short = re.sub(r"[（(][^）)]*[）)]", "", ja).strip()
    short = re.sub(r"\s+", "", short)
    return short[:6]

def build_output(online: dict[str, dict], local: dict[str, dict]):
    lines = ["export const MACHINES = ["]
    changes, added = [], []

    for cost in [3000, 2500, 2000, 1500]:
        lines.append(f"  // ══════════ {cost} COST ══════════")
        for tier in ["S", "A+", "A", "A-", "B+", "B", "B-", "C", "Z"]:
            group = [(i, o) for i, o in online.items() if o["cost"] == cost and o["tier"] == tier]
            if not group:
                continue
            lines.append(f"  // {tier}")
            for id_num, o in group:
                if id_num in local:
                    l = local[id_num]
                    if (l["tier"], l["cost"]) != (tier, cost):
                        changes.append(f"  m{id_num}  {l['name']}: {l['cost']}/{l['tier']} → {cost}/{tier}")
                    name, short = l["name"], l["short"]
                    img, link = l["img"], l["link"]
                elif id_num in NEW_MACHINES:
                    meta = NEW_MACHINES[id_num]
                    name = meta["name"].replace("'", "\\'")
                    short = make_short(meta["ja"]).replace("'", "\\'")
                    img = f"/images/machines/{id_num}.png"
                    link = meta["link"]
                    added.append(f"  m{id_num}  [{cost}/{tier}]  {name}")
                else:
                    print(f"  [WARN] 新机体 m{id_num}（{o['ja']}）缺少元数据，已跳过——"
                          f"请在 NEW_MACHINES 中补充")
                    continue
                lines.append(
                    f"  {{ id: 'm{id_num}', name: '{name}', short: '{short}', "
                    f"cost: {cost}, tier: '{tier}', img: '{img}', link: '{link}' }},")

    lines += ["]", "", "export const TIERS = ['S', 'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C']", "",
              "export const TIER_META = {",
              "  'S':  { label: 'S',  sub: '最強',   cls: 's'     },",
              "  'A+': { label: 'A+', sub: '',        cls: 'aplus'  },",
              "  'A':  { label: 'A',  sub: '',        cls: 'a'      },",
              "  'A-': { label: 'A-', sub: '',        cls: 'aminus' },",
              "  'B+': { label: 'B+', sub: '',        cls: 'bplus'  },",
              "  'B':  { label: 'B',  sub: '',        cls: 'b'      },",
              "  'B-': { label: 'B-', sub: '',        cls: 'bminus' },",
              "  'C':  { label: 'C',  sub: '要強化',  cls: 'c'      },",
              "}"]
    return "\n".join(lines) + "\n", changes, added

# ─── 入口 ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="以线上榜单更新 machines.js（保留 link/中文名/本地图片）")
    parser.add_argument("--dry-run", action="store_true", help="只打印变更，不写文件")
    args = parser.parse_args()

    online = parse_online(fetch_rank_html())
    local = parse_local()
    print(f"  线上 {len(online)} 台 / 本地 {len(local)} 台")

    missing = sorted(set(local) - set(online))
    for i in missing:
        print(f"  [WARN] 本地机体 m{i}（{local[i]['name']}）不在榜单上，已从列表移除")

    output, changes, added = build_output(online, local)

    print(f"\n新增 {len(added)} 台:")
    print("\n".join(added) or "  （无）")
    print(f"\n变动 {len(changes)} 处:")
    print("\n".join(changes[:15]) + ("\n  ..." if len(changes) > 15 else "") or "  （无）")

    if args.dry_run:
        print("\n[dry-run] 未写文件")
        return

    MACHINES_JS.write_text(output, encoding="utf-8")
    print(f"\n[OK] 已写入 {MACHINES_JS}")

if __name__ == "__main__":
    main()
