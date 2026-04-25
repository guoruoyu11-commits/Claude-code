# 基于 content_nodes 的节点翻译脚本：只提取纯文本送 Gemini，跳过 HTML 标签。
#
# 流程：
#   1. 加载 {id}.json；若无 content_nodes，先调用 html_to_nodes 生成
#   2. 深拷贝节点树
#   3. 遍历节点，收集含日文的文本引用
#   4. 字典预替换（固定术语直接命中，不走 Gemini）
#   5. 剩余文本分批（≤4000字符/批），以 JSON 数组发给 Gemini
#   6. 解析返回 JSON 数组，写回节点
#   7. 断点续传；全部完成后保存 {id}_zh.json
#
# 用法：
#   py scripts/translate_nodes.py m12504
#   py scripts/translate_nodes.py m12504 --force
#   py scripts/translate_nodes.py m12504 --model gemini-2.0-flash

import sys
import json
import copy
import time
import re
import argparse
import os
from datetime import datetime, timezone
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("缺少依赖，请先运行：pip install beautifulsoup4")
    sys.exit(1)

try:
    from google import genai
except ImportError:
    print("缺少依赖，请先运行：pip install google-genai")
    sys.exit(1)

# 加载 .env
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    for _line in _env_path.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

BASE_DIR   = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "public" / "data" / "machines"
DEFAULT_PROMPT_FILE = BASE_DIR / "prompt_nodes.txt"

# ── 导入本项目工具 ──────────────────────────────────────────────

sys.path.insert(0, str(Path(__file__).parent))
from html_to_nodes import html_to_nodes
from ja_zh_dict import has_japanese, apply_dict


# ── 节点树遍历 ──────────────────────────────────────────────────

def collect_refs(nodes: list, refs: list):
    """
    递归遍历节点树，收集所有含日文文本的引用。
    ref 格式：{"node": <dict>, "key": "v" | "label"}
    直接操作传入的 refs 列表（in-place append）。
    """
    for node in nodes:
        tag = node.get("t", "")
        if tag == "br":
            continue

        for key in ("v", "label"):
            val = node.get(key)
            if isinstance(val, str) and has_japanese(val):
                refs.append({"node": node, "key": key})

        children = node.get("c")
        if isinstance(children, list):
            collect_refs(children, refs)


# ── Gemini 调用 ─────────────────────────────────────────────────

_MICRO_BATCH_PROMPT = (
    "将以下 JSON 数组中的日文字符串翻译成中文（简体），"
    "游戏专有名词使用中文惯用译名。"
    "直接输出相同长度的 JSON 字符串数组，不要加任何说明或代码块标记。\n\n{texts}"
)


def _call_gemini_raw(texts: list[str], _unused_template, client, model_name: str, retries: int = 2) -> list[str] | None:
    """Positional 格式（plain string array）：用于缺失条目的微批次补译。"""
    texts_json = json.dumps(texts, ensure_ascii=False)
    prompt = _MICRO_BATCH_PROMPT.replace("{texts}", texts_json)
    for attempt in range(retries):
        try:
            response = client.models.generate_content(model=model_name, contents=prompt)
            raw = response.text.strip()
            raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
            raw = re.sub(r"\s*```$", "", raw)
            result = json.loads(raw)
            if isinstance(result, list) and len(result) == len(texts):
                return [str(r) for r in result]
            return None
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(5 * (2 ** attempt))
            else:
                return None
    return None


def translate_batch(
    texts: list[str],
    prompt_template: str,
    client,
    model_name: str,
    retries: int = 3,
) -> list[str] | None:
    """
    ID 格式：发送 {id, t} 数组，按 id 匹配响应。
    Gemini 少返回条目时自动补译，保证返回等长列表。
    网络/解析完全失败时返回 None。
    """
    tagged = [{"id": i, "t": t} for i, t in enumerate(texts)]
    texts_json = json.dumps(tagged, ensure_ascii=False)
    prompt = prompt_template.replace("{texts}", texts_json)

    for attempt in range(retries):
        try:
            response = client.models.generate_content(model=model_name, contents=prompt)
            raw = response.text.strip()
            raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
            raw = re.sub(r"\s*```$", "", raw)
            result = json.loads(raw)

            # 按 id 匹配
            id_map: dict[int, str] = {}
            if isinstance(result, list):
                for item in result:
                    if isinstance(item, dict) and "id" in item and "t" in item:
                        try:
                            id_map[int(item["id"])] = str(item["t"])
                        except (ValueError, TypeError):
                            pass

            if not id_map:
                # 格式完全错误，重试
                if attempt < retries - 1:
                    wait = 5 * (2 ** attempt)
                    print(f"\n  [RETRY {attempt+1}/{retries-1}] {wait}s 后重试（格式错误）...", flush=True)
                    time.sleep(wait)
                    continue
                return None

            missing = [i for i in range(len(texts)) if i not in id_map]
            if missing:
                print(f"\n  [WARN] {len(missing)} 条缺失，补译中...", end=" ", flush=True)
                for chunk_start in range(0, len(missing), 20):
                    chunk_ids = missing[chunk_start:chunk_start + 20]
                    chunk_texts = [texts[i] for i in chunk_ids]
                    chunk_result = _call_gemini_raw(chunk_texts, prompt_template, client, model_name)
                    if chunk_result:
                        for idx, translated in zip(chunk_ids, chunk_result):
                            id_map[idx] = translated
                still_missing = [i for i in range(len(texts)) if i not in id_map]
                if still_missing:
                    print(f"[WARN] 仍缺失 {len(still_missing)} 条，保留原文")
                    for i in still_missing:
                        id_map[i] = texts[i]

            return [id_map[i] for i in range(len(texts))]

        except Exception as e:
            if attempt < retries - 1:
                wait = 5 * (2 ** attempt)
                print(f"\n  [RETRY {attempt+1}/{retries-1}] {wait}s 后重试... ({e})", flush=True)
                time.sleep(wait)
            else:
                print(f"  [ERR] Gemini 调用失败: {e}")
                return None
    return None


# ── 进度存档 ────────────────────────────────────────────────────

def _progress_path(machine_id: str) -> Path:
    return OUTPUT_DIR / f"{machine_id}_zh_nodes_progress.json"


def _load_progress(machine_id: str) -> dict | None:
    p = _progress_path(machine_id)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _save_progress(machine_id: str, batches: list[list[str]], translated: dict[int, list[str]]):
    _progress_path(machine_id).write_text(
        json.dumps({"batches": batches, "translated": translated}, ensure_ascii=False),
        encoding="utf-8",
    )


def _delete_progress(machine_id: str):
    p = _progress_path(machine_id)
    if p.exists():
        p.unlink()


# ── 分批 ────────────────────────────────────────────────────────

def make_batches(texts: list[str], max_chars: int = 4000, max_items: int = 100) -> list[list[str]]:
    """将文本列表按字符总量和条目数分批，每批不超过 max_chars 字符且不超过 max_items 条。"""
    batches: list[list[str]] = []
    buf: list[str] = []
    buf_len = 0
    for t in texts:
        if buf and (buf_len + len(t) > max_chars or len(buf) >= max_items):
            batches.append(buf)
            buf, buf_len = [], 0
        buf.append(t)
        buf_len += len(t)
    if buf:
        batches.append(buf)
    return batches


# ── 核心函数 ────────────────────────────────────────────────────

def translate_one_nodes(
    machine_id: str,
    prompt_file: str | Path = DEFAULT_PROMPT_FILE,
    model_name: str = "gemini-2.5-flash",
    delay: float = 1.0,
    force: bool = False,
) -> dict | None:
    """
    翻译单个机体的节点树并保存 _zh.json。
    返回：{"status": "skipped"} / {"status": "ok", ...} / None（失败）
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    src_path = OUTPUT_DIR / f"{machine_id}.json"
    out_path = OUTPUT_DIR / f"{machine_id}_zh.json"

    if not force and out_path.exists():
        src = json.loads(src_path.read_text(encoding="utf-8"))
        for sp in src.get("sub_pages", []):
            sub_id = sp["file"]
            if not (OUTPUT_DIR / f"{sub_id}_zh.json").exists():
                print(f"  >> 补翻缺失子页面: {sp['name']} ({sub_id})")
                translate_one_nodes(sub_id, prompt_file, model_name, delay, force)
        return {"status": "skipped"}

    if not src_path.exists():
        print(f"[ERR] 源文件不存在: {src_path}")
        return None

    src = json.loads(src_path.read_text(encoding="utf-8"))

    # 确保 content_nodes 存在
    if "content_nodes" not in src:
        content_html = src.get("content_html", "")
        if not content_html:
            print(f"[ERR] {machine_id}.json 中 content_html 为空")
            return None
        print(f"  [INFO] 生成 content_nodes ...", end=" ", flush=True)
        nodes_src = html_to_nodes(content_html)
        src["content_nodes"] = nodes_src
        src_path.write_text(
            json.dumps(src, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        print("完成")
    else:
        nodes_src = src["content_nodes"]

    # 读提示词
    prompt_path = Path(prompt_file)
    if not prompt_path.exists():
        print(f"[ERR] 提示词文件不存在: {prompt_path}")
        return None
    prompt_template = prompt_path.read_text(encoding="utf-8")
    if "{texts}" not in prompt_template:
        print("[ERR] prompt 文件中必须包含 {texts} 占位符")
        return None

    # 初始化 Gemini
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[ERR] 未设置 GEMINI_API_KEY，请在 .env 文件中填写")
        return None
    client = genai.Client(api_key=api_key)

    # 深拷贝节点树（不修改源数据）
    nodes_zh = copy.deepcopy(nodes_src)

    # 收集所有含日文文本的引用
    refs: list[dict] = []
    collect_refs(nodes_zh, refs)

    # 字典预替换
    dict_hit = 0
    dict_log: list[dict] = []
    pending_refs: list[dict] = []
    for ref in refs:
        original = ref["node"][ref["key"]]
        translated, hit = apply_dict(original)
        if hit:
            dict_log.append({
                "source": original,
                "target": translated,
                "method": "dict",
                "node_type": ref["node"].get("t", "#"),
            })
            ref["node"][ref["key"]] = translated
            dict_hit += 1
        else:
            pending_refs.append(ref)

    pending_texts = [r["node"][r["key"]] for r in pending_refs]
    total_chars   = sum(len(t) for t in pending_texts)
    print(f"  字典命中 {dict_hit} 条，待翻译 {len(pending_texts)} 条（{total_chars} 字符）")

    if not pending_texts:
        # 全部字典命中，直接保存
        data = _build_output(machine_id, src, nodes_zh, model_name, translation_log=dict_log)
        out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return data

    # 加载进度或重新分批
    progress = None if force else _load_progress(machine_id)
    if progress:
        batches   = progress["batches"]
        done_map: dict[int, list[str]] = {int(k): v for k, v in progress["translated"].items()}
        resumed   = len(done_map)
        print(f"  检测到进度文件，已完成 {resumed}/{len(batches)} 批，从第 {resumed+1} 批继续...")
    else:
        batches  = make_batches(pending_texts)
        done_map = {}
        if force:
            _delete_progress(machine_id)

    total_batches = len(batches)
    print(f"  共 {total_batches} 批，开始翻译...")

    # 逐批翻译
    global_offset = 0
    batch_offsets: list[int] = []
    for b in batches:
        batch_offsets.append(global_offset)
        global_offset += len(b)

    for i, batch in enumerate(batches):
        if i in done_map:
            print(f"  [{i+1:2}/{total_batches}] 跳过（已完成）")
            continue
        chars = sum(len(t) for t in batch)
        print(f"  [{i+1:2}/{total_batches}] {len(batch)} 条，{chars} 字符...", end=" ", flush=True)
        result = translate_batch(batch, prompt_template, client, model_name)
        if result is None:
            print("[FAIL]")
            _save_progress(machine_id, batches, {str(k): v for k, v in done_map.items()})
            print(f"  进度已保存，重新运行可从第 {i+2} 批继续")
            return None
        done_map[i] = result
        _save_progress(machine_id, batches, {str(k): v for k, v in done_map.items()})
        print("[OK]")
        if i < total_batches - 1:
            time.sleep(delay)

    # 将翻译结果写回节点引用，同时记录翻译日志
    gemini_log: list[dict] = []
    for i, batch_result in sorted(done_map.items()):
        offset = batch_offsets[i]
        for j, translated_text in enumerate(batch_result):
            ref = pending_refs[offset + j]
            original = pending_texts[offset + j]
            gemini_log.append({
                "source": original,
                "target": translated_text,
                "method": "gemini",
                "node_type": ref["node"].get("t", "#"),
            })
            ref["node"][ref["key"]] = translated_text

    # 保存最终文件
    data = _build_output(machine_id, src, nodes_zh, model_name, translation_log=dict_log + gemini_log)
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    _delete_progress(machine_id)

    # 跟随翻译子页面
    sub_pages = src.get("sub_pages", [])
    if sub_pages:
        # _build_output 已经通过 _strip_nav_row 提取了中文名，优先使用
        translated_names = {s["file"]: s["name"] for s in data.get("sub_pages", [])}
        # _strip_nav_row 未能从导航行提取时（仍为日文），回退到翻译日志查找
        log_lookup = {e["source"]: e["target"] for e in dict_log + gemini_log}
        sub_pages_zh = []
        for sp in sub_pages:
            sub_id = sp["file"]
            print(f"  >> 翻译子页面: {sp['name']} ({sub_id})")
            sub_result = translate_one_nodes(sub_id, prompt_file, model_name, delay, force)
            if sub_result and sub_result.get("status") != "skipped":
                print(f"  [OK] 子页面已保存: {sub_id}_zh.json")
            elif sub_result and sub_result.get("status") == "skipped":
                print(f"  -- 子页面已存在，跳过: {sub_id}")
            name = translated_names.get(sub_id, sp["name"])
            if has_japanese(name):
                name = log_lookup.get(sp["name"], name)
            sub_pages_zh.append({"name": name, "file": sub_id, "url": sp["url"]})
        data["sub_pages"] = sub_pages_zh
        out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return data


def _strip_wiki_h2(nodes: list) -> list:
    """移除顶部多级面包屑 h2（含多个 atwiki 链接和 '>' 分隔符）。
    单链接 h2（机体名标题）保留。"""
    if not nodes or nodes[0].get("t") != "h2":
        return nodes
    children = nodes[0].get("c", [])
    link_count = 0
    for c in children:
        if c.get("t") == "a" and "/exvs2infiniteboost/pages/" in c.get("a", {}).get("href", ""):
            link_count += 1
        elif c.get("t") == "#" and c.get("v", "").strip() in (">", "＞", " > ", "　>　"):
            continue
        else:
            return nodes  # 含其他内容，不剥除
    return nodes[1:] if link_count > 1 else nodes


def _strip_nav_row(nodes: list, sub_pages_raw: list) -> tuple[list, list]:
    """
    检测并移除节点树顶部的子页面导航行（由工具栏替代），
    同时从翻译后的链接文本中提取中文子页面名称。
    返回 (清理后的 nodes, 更新的 sub_pages)
    """
    url_map = {sp["url"]: sp for sp in sub_pages_raw}
    nav_idx = None
    updated = []

    for i, node in enumerate(nodes):
        if node.get("t") != "div":
            continue
        kids = node.get("c", [])
        if len(kids) != 1 or kids[0].get("t") != "span":
            continue
        span = kids[0]
        if "font-size" not in span.get("a", {}).get("style", ""):
            continue
        span_kids = span.get("c", [])
        has_bold = any(
            c.get("t") == "span" and "font-weight" in c.get("a", {}).get("style", "")
            for c in span_kids
        )
        has_wiki_link = any(
            c.get("t") == "a" and "/exvs2infiniteboost/pages/" in c.get("a", {}).get("href", "")
            for c in span_kids
        )
        if not (has_bold and has_wiki_link):
            continue

        # 从链接中提取中文名称
        if url_map:
            for c in span_kids:
                if c.get("t") != "a":
                    continue
                href = c.get("a", {}).get("href", "")
                full = "https:" + href if href.startswith("//") else href
                if full in url_map:
                    sp = url_map[full]
                    updated.append({"name": c.get("v", sp["name"]), "file": sp["file"], "url": sp["url"]})
        nav_idx = i
        break

    cleaned = [n for i, n in enumerate(nodes) if i != nav_idx]
    return cleaned, updated if updated else sub_pages_raw


def _build_output(machine_id: str, src: dict, nodes_zh: list, model_name: str, translation_log: list | None = None) -> dict:
    sub_pages_raw = src.get("sub_pages", [])
    nodes_clean, sub_pages_zh = _strip_nav_row(_strip_wiki_h2(nodes_zh), sub_pages_raw)
    result = {
        "status": "ok",
        "id": machine_id,
        "name": src.get("name", ""),
        "translated_at": datetime.now(timezone.utc).isoformat(),
        "source_id": machine_id,
        "model": model_name,
        "content_nodes": nodes_clean,
    }
    if sub_pages_zh:
        result["sub_pages"] = sub_pages_zh
    if translation_log:
        result["translation_log"] = translation_log
    return result


# ── CLI ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="基于节点树翻译单个机体页面（日文→中文）")
    parser.add_argument("id",       type=str,                              help="机体 ID，如 m12504")
    parser.add_argument("--prompt", type=str, default=str(DEFAULT_PROMPT_FILE), help="提示词文件路径（默认 prompt_nodes.txt）")
    parser.add_argument("--model",  type=str, default="gemini-2.5-flash",   help="Gemini 模型名（默认 gemini-2.5-flash）")
    parser.add_argument("--delay",  type=float, default=1.0,              help="批间等待秒数（默认 1.0）")
    parser.add_argument("--force",  action="store_true",                  help="覆盖已有译文")
    args = parser.parse_args()

    print(f">> 翻译 {args.id}")
    result = translate_one_nodes(
        args.id,
        prompt_file=args.prompt,
        model_name=args.model,
        delay=args.delay,
        force=args.force,
    )

    if result is None:
        print("[FAIL] 翻译失败")
        sys.exit(1)
    elif result.get("status") == "skipped":
        print("-- 已存在，跳过（使用 --force 强制重新翻译）")
    else:
        print(f"[OK] 已保存至 {OUTPUT_DIR / (args.id + '_zh.json')}")


if __name__ == "__main__":
    main()
