"""
将机体 JSON 文件中的 content_html 转换为结构化节点树 content_nodes。

节点格式：
  元素节点：{"t": "tagname", "a": {...attrs}, "c": [...children]}
  叶文本节点：{"t": "#", "v": "text"}
  内联文本元素：{"t": "td", "a": {...}, "v": "text"}   ← 唯一子节点为文本时直接提升
  换行合并元素：{"t": "div", "v": "第1段\n第2段"}        ← text+br+text 序列合并为 \n
  折叠块：  {"t": "collapse", "label": "目次", "open": true, "c": [...]}

优化：
  1. 内联单文本子节点：若元素唯一子节点为 # 文本，则提升到父节点的 "v" 字段
  2. br 换行合并：连续 text+br+text 序列合并为单个 # 节点，用 \n 连接

用法：
  py scripts/html_to_nodes.py m12504
  py scripts/html_to_nodes.py m12504 --force
  py scripts/html_to_nodes.py --all
"""

import re
import sys
import json
import argparse
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Comment, Tag

_ATWIKI_IMG = re.compile(r'(?:https?:)?//img\.atwiki\.jp/[^\s"\'<>\\]+')

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR   = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "public" / "data" / "machines"

# 跳过这些 class 的元素（广告占位等）
SKIP_CLASSES = {"atwiki-ads-margin", "atwiki_autoads"}

# 保留的属性列表（过滤掉 js 事件等）
KEEP_ATTRS = {
    "id", "class", "style", "href", "target", "rel",
    "src", "alt", "width", "height", "srcset", "type", "media",
    "rowspan", "colspan", "bgcolor", "align", "valign", "title",
    "name",
}


def _has_skip_class(tag: Tag) -> bool:
    classes = tag.get("class") or []
    return any(c in SKIP_CLASSES or c.startswith("atwiki_autoads") for c in classes)


def _build_attrs(tag: Tag) -> dict:
    attrs = {}
    for k, v in tag.attrs.items():
        if k not in KEEP_ATTRS:
            continue
        if isinstance(v, list):
            v = " ".join(v)
        attrs[k] = v
    return attrs


def _merge_br_text(children: list) -> list:
    """将 [#text, br, #text, ...] 序列合并为单个 #text 节点，用 \\n 连接。"""
    result = []
    i = 0
    while i < len(children):
        c = children[i]
        if c["t"] == "#":
            parts = [c["v"].strip("\n")]
            j = i + 1
            # 贪婪：只要后面还有 br + text 就继续吸收
            while j + 1 < len(children) and children[j]["t"] == "br" and children[j + 1]["t"] == "#":
                parts.append(children[j + 1]["v"].strip("\n"))
                j += 2
            if len(parts) > 1:
                result.append({"t": "#", "v": "\n".join(parts)})
                i = j
            else:
                result.append(c)
                i += 1
        else:
            result.append(c)
            i += 1
    return result


def _inline_single_text(node: dict) -> dict:
    """若元素唯一子节点是 # 文本，将其提升为父节点的 "v"，删除 "c"。"""
    children = node.get("c", [])
    if len(children) == 1 and children[0]["t"] == "#":
        node["v"] = children[0]["v"]
        del node["c"]
    return node


def node_from_tag(tag) -> dict | None:
    """递归将 BeautifulSoup 节点转换为 JSON 节点，跳过注释和广告。"""
    # 注释节点 — 跳过
    if isinstance(tag, Comment):
        return None

    # 文本节点
    if isinstance(tag, NavigableString):
        text = str(tag)
        # 跳过纯空白（只含换行/空格）
        if not text.strip():
            return None
        return {"t": "#", "v": text}

    if not isinstance(tag, Tag):
        return None

    # 广告容器 — 跳过
    if _has_skip_class(tag):
        return None

    tag_name = tag.name.lower()

    # plugin-openclose 折叠块
    if "plugin-openclose" in (tag.get("class") or []):
        link_el = tag.find(class_="plugin-openclose-link")
        contents_el = tag.find(class_="plugin-openclose-contents")

        label_text = ""
        if link_el:
            a = link_el.find("a")
            label_text = (a.get_text() if a else link_el.get_text()).strip()

        # 判断初始展开状态
        open_state = True
        if contents_el:
            style = contents_el.get("style", "")
            open_state = "display: none" not in style and "display:none" not in style

        inner_children = []
        if contents_el:
            for child in contents_el.children:
                n = node_from_tag(child)
                if n is not None:
                    inner_children.append(n)

        # 对折叠内容也做合并优化
        inner_children = _merge_br_text(inner_children)

        node = {"t": "collapse", "label": label_text, "open": open_state}
        if inner_children:
            node["c"] = inner_children
        return node

    # 普通元素
    attrs = _build_attrs(tag)

    children = []
    for child in tag.children:
        n = node_from_tag(child)
        if n is not None:
            children.append(n)

    # 优化 1：br 换行合并
    children = _merge_br_text(children)

    node = {"t": tag_name}
    if attrs:
        node["a"] = attrs
    if children:
        node["c"] = children

    # 优化 2：内联单文本子节点
    _inline_single_text(node)

    return node


def _rewrite_img_src(nodes: list, local_img: str) -> None:
    """Recursively replace atwiki image src with local machine image path."""
    for node in nodes:
        if not isinstance(node, dict):
            continue
        if node.get("t") == "img":
            attrs = node.get("a", {})
            src = attrs.get("src", "")
            if _ATWIKI_IMG.match(src):
                attrs["src"] = local_img
        _rewrite_img_src(node.get("c", []), local_img)


def html_to_nodes(content_html: str) -> list:
    """将 content_html 解析为节点树列表。"""
    soup = BeautifulSoup(content_html, "html.parser")
    root = soup.find()  # 外层 div.box#wikibody
    if root is None:
        return []

    nodes = []
    for child in root.children:
        n = node_from_tag(child)
        if n is not None:
            nodes.append(n)
    return nodes


def process_one(machine_id: str, force: bool = False) -> bool:
    path = OUTPUT_DIR / f"{machine_id}.json"
    if not path.exists():
        print(f"[SKIP] {path} 不存在")
        return False

    data = json.loads(path.read_text(encoding="utf-8"))

    if "content_nodes" in data and not force:
        print(f"[SKIP] {machine_id} 已有 content_nodes（用 --force 覆盖）")
        return False

    html = data.get("content_html", "")
    if not html:
        print(f"[SKIP] {machine_id} content_html 为空")
        return False

    print(f"[CONV] {machine_id} ...", end=" ", flush=True)
    nodes = html_to_nodes(html)
    num = machine_id.split("_")[0].lstrip("m")
    _rewrite_img_src(nodes, f"/images/machines/{num}.png")
    data["content_nodes"] = nodes
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    size_kb = path.stat().st_size // 1024
    print(f"完成（{len(nodes)} 顶层节点，{size_kb} KB）")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("id", nargs="?", help="机体 ID，如 m12504")
    parser.add_argument("--all", action="store_true", help="处理所有 JSON 文件")
    parser.add_argument("--force", action="store_true", help="覆盖已有 content_nodes")
    args = parser.parse_args()

    if args.all:
        files = sorted(OUTPUT_DIR.glob("m*.json"))
        # 排除 _zh.json 和 _zh_progress.json
        files = [f for f in files if "_zh" not in f.stem]
        for f in files:
            process_one(f.stem, force=args.force)
    elif args.id:
        process_one(args.id, force=args.force)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
