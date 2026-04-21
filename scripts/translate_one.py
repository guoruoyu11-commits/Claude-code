# 使用 Gemini API 翻译单个机体页面（日文 HTML → 中文 HTML）。
#
# 使用方法：
#   py translate_one.py m12504
#   py translate_one.py m12504 --force
#   py translate_one.py m12504 --prompt my_prompt.txt --model gemini-2.0-flash
#
# 依赖：pip install google-genai beautifulsoup4
# API Key：在 .env 文件中设置 GEMINI_API_KEY=你的key

import re
import sys
import json
import time
import argparse
import os
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
    from google import genai
    from google.genai import types as genai_types
except ImportError:
    print("缺少依赖，请先运行：pip install google-genai")
    sys.exit(1)

# 从项目根目录的 .env 文件加载环境变量（优先级低于系统环境变量）
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    for _line in _env_path.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

# ─── 路径 ────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "public" / "data" / "machines"
DEFAULT_PROMPT_FILE = BASE_DIR / "prompt.txt"

# ─── 分段 ─────────────────────────────────────────────────────

def _collect_chunks(nodes, max_chars: int) -> list[str]:
    chunks: list[str] = []
    buf: list[str] = []
    buf_len = 0
    for node in nodes:
        s = str(node)
        if len(s) <= max_chars:
            if buf and buf_len + len(s) > max_chars:
                chunks.append("".join(buf))
                buf, buf_len = [], 0
            buf.append(s)
            buf_len += len(s)
        else:
            # 单个节点超限 — 递归下沉到其子节点
            if buf:
                chunks.append("".join(buf))
                buf, buf_len = [], 0
            children = list(getattr(node, "children", []))
            if children:
                chunks.extend(_collect_chunks(children, max_chars))
            else:
                chunks.append(s)  # 无法再拆分，原样保留
    if buf:
        chunks.append("".join(buf))
    return chunks


def chunk_html(content_html: str, max_chars: int = 6000) -> list[str]:
    """
    将 HTML 按节点递归分组，每组不超过 max_chars 字符。
    超大单节点会递归拆分其子节点，保证不会传送超大文本块。
    """
    soup = BeautifulSoup(content_html, "html.parser")
    root = soup.find()
    if root is None:
        return [content_html]
    return _collect_chunks(list(root.children), max_chars)


# ─── Gemini 调用 ───────────────────────────────────────────────

def translate_chunk(chunk_html: str, prompt_template: str, client, model_name: str, retries: int = 3) -> str | None:
    """
    将提示词中的 {html} 替换为当前片段，调用 Gemini，返回翻译后的 HTML 字符串。
    自动重试最多 retries 次，失败返回 None。
    """
    prompt = prompt_template.replace("{html}", chunk_html)
    for attempt in range(retries):
        try:
            response = client.models.generate_content(model=model_name, contents=prompt)
            text = response.text.strip()
            # 去除模型可能包裹的 markdown 代码块（```html ... ```）
            text = re.sub(r'^```(?:html)?\s*', '', text, flags=re.IGNORECASE)
            text = re.sub(r'\s*```$', '', text)
            return text
        except Exception as e:
            if attempt < retries - 1:
                wait = 5 * (2 ** attempt)  # 5s, 10s, 20s
                print(f"\n  [RETRY {attempt+1}/{retries-1}] {wait}s 后重试... ({e})", flush=True)
                time.sleep(wait)
            else:
                print(f"  [ERR] Gemini 调用失败: {e}")
                return None


# ─── 进度存档 ──────────────────────────────────────────────────

def _progress_path(machine_id: str) -> Path:
    return OUTPUT_DIR / f"{machine_id}_zh_progress.json"


def _load_progress(machine_id: str) -> dict | None:
    """读取进度文件，返回 {chunks, translated} 或 None（不存在时）。"""
    p = _progress_path(machine_id)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _save_progress(machine_id: str, chunks: list[str], translated: dict[int, str]):
    """将当前进度写入临时文件，translated 键为字符串化的段索引。"""
    _progress_path(machine_id).write_text(
        json.dumps({"chunks": chunks, "translated": translated}, ensure_ascii=False),
        encoding="utf-8",
    )


def _delete_progress(machine_id: str):
    p = _progress_path(machine_id)
    if p.exists():
        p.unlink()


# ─── 核心函数 ──────────────────────────────────────────────────

def translate_one(
    machine_id: str,
    prompt_file: str | Path = DEFAULT_PROMPT_FILE,
    model_name: str = "gemini-2.5-pro",
    delay: float = 1.0,
    force: bool = False,
) -> dict | None:
    """
    翻译并保存单个机体页面。支持断点续传：中途失败后重新运行会从上次中断处继续。

    返回值：
      {"status": "skipped"}  — _zh.json 已存在且 force=False
      {"status": "ok", ...}  — 翻译完成，已保存
      None                   — 失败
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    src_path = OUTPUT_DIR / f"{machine_id}.json"
    out_path = OUTPUT_DIR / f"{machine_id}_zh.json"

    if not force and out_path.exists():
        return {"status": "skipped"}

    # 读源文件
    if not src_path.exists():
        print(f"[ERR] 源文件不存在: {src_path}")
        return None

    src = json.loads(src_path.read_text(encoding="utf-8"))
    content_html = src.get("content_html", "")
    if not content_html:
        print(f"[ERR] {machine_id}.json 中 content_html 为空")
        return None

    # 读提示词
    prompt_path = Path(prompt_file)
    if not prompt_path.exists():
        print(f"[ERR] 提示词文件不存在: {prompt_path}")
        print("      请创建 prompt.txt，内容中用 {{html}} 作为 HTML 片段占位符")
        return None
    prompt_template = prompt_path.read_text(encoding="utf-8")
    if "{html}" not in prompt_template:
        print("[ERR] prompt.txt 中必须包含 {html} 占位符")
        return None

    # 初始化 Gemini
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[ERR] 未设置 GEMINI_API_KEY，请在 .env 文件中填写")
        return None
    client = genai.Client(api_key=api_key)

    # 加载进度或重新分段
    progress = None if force else _load_progress(machine_id)
    if progress:
        chunks = progress["chunks"]
        translated: dict[int, str] = {int(k): v for k, v in progress["translated"].items()}
        resumed = len(translated)
        print(f"  检测到进度文件，已完成 {resumed}/{len(chunks)} 段，从第 {resumed+1} 段继续...")
    else:
        chunks = chunk_html(content_html)
        translated = {}
        if force:
            _delete_progress(machine_id)

    total = len(chunks)
    print(f"  共 {total} 段，开始翻译...")

    for i, chunk in enumerate(chunks):
        if i in translated:
            print(f"  [{i+1:2}/{total}] 跳过（已完成）")
            continue
        print(f"  [{i+1:2}/{total}] {len(chunk)} 字符...", end=" ", flush=True)
        result = translate_chunk(chunk, prompt_template, client, model_name)
        if result is None:
            print("[FAIL]")
            # 保存当前进度后退出
            _save_progress(machine_id, chunks, {str(k): v for k, v in translated.items()})
            print(f"  进度已保存，重新运行可从第 {i+2} 段继续")
            return None
        translated[i] = result
        # 每段成功后立即持久化进度
        _save_progress(machine_id, chunks, {str(k): v for k, v in translated.items()})
        print("[OK]")
        if i < total - 1:
            time.sleep(delay)

    # 全部完成，合并写入最终文件
    combined_html = "<div>" + "".join(translated[i] for i in range(total)) + "</div>"

    data = {
        "status": "ok",
        "id": machine_id,
        "name": src.get("name", ""),
        "translated_at": datetime.now(timezone.utc).isoformat(),
        "source_id": machine_id,
        "model": model_name,
        "content_html": combined_html,
    }

    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    _delete_progress(machine_id)
    return data


# ─── CLI ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="用 Gemini API 翻译单个机体攻略页面")
    parser.add_argument("id",       type=str,                           help="机体 ID，如 m12504")
    parser.add_argument("--prompt", type=str, default=str(DEFAULT_PROMPT_FILE), help="提示词文件路径（默认 prompt.txt）")
    parser.add_argument("--model",  type=str, default="gemini-2.5-pro", help="Gemini 模型名（默认 gemini-2.5-pro）")
    parser.add_argument("--delay",  type=float, default=1.0,            help="段间等待秒数（默认 1.0）")
    parser.add_argument("--force",  action="store_true",                help="覆盖已有译文")
    args = parser.parse_args()

    print(f">> 翻译 {args.id}")
    result = translate_one(
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
