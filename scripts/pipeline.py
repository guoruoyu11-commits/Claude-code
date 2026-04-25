# 单机体全流程：抓取 → 节点化 → 翻译 → 本地化图片
#
# 用法：
#   py scripts/pipeline.py m13501
#   py scripts/pipeline.py m13501 --force
#   py scripts/pipeline.py m13501 --model gemini-2.5-flash
#   py scripts/pipeline.py m13501 --skip-scrape         # 跳过抓取，直接翻译
#   py scripts/pipeline.py m13501 m12504 --workers 3    # 3 子进程并发
#   py scripts/pipeline.py m13501 --retries 3           # 失败后最多重试 3 次（默认 2）

import sys
import argparse
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))

_print_lock = threading.Lock()


# ── 单机体步骤（仅在 --_single 模式下直接调用）─────────────────────

def step_scrape(machine_id: str, force: bool) -> bool:
    print(f"[{machine_id}] [1/3] 抓取...")
    from scrape_one import scrape_one
    result = scrape_one(machine_id, force=force)
    if result is None:
        print(f"[{machine_id}] [FAIL] 抓取失败")
        return False
    print(f"[{machine_id}] [1/3] 抓取完成")
    return True


def step_translate(machine_id: str, force: bool, model: str) -> bool:
    print(f"[{machine_id}] [2/3] 翻译...")
    from translate_nodes import translate_one_nodes
    result = translate_one_nodes(machine_id, force=force, model_name=model)
    if result is None:
        print(f"[{machine_id}] [FAIL] 翻译失败")
        return False
    print(f"[{machine_id}] [2/3] 翻译完成")
    return True


def step_localize(machine_id: str) -> bool:
    print(f"[{machine_id}] [3/3] 本地化图片...")
    from localize_wiki_images import process_file
    output_dir = BASE_DIR / "public" / "data" / "machines"
    total = 0
    for suffix in [f"{machine_id}.json", f"{machine_id}_zh.json"]:
        path = output_dir / suffix
        if path.exists():
            count = process_file(path)
            if count:
                print(f"[{machine_id}]   替换 {count} 处: {suffix}")
            total += count
    print(f"[{machine_id}] [3/3] 图片本地化完成（{total} 处）")
    return True


def run_single(machine_id: str, force: bool, model: str, skip_scrape: bool) -> bool:
    """在当前进程内顺序执行单个机体的全流程（由子进程调用）。"""
    print(f"[{machine_id}] 开始全流程 (model={model})")
    if not skip_scrape:
        if not step_scrape(machine_id, force):
            return False
    if not step_translate(machine_id, force, model):
        return False
    step_localize(machine_id)
    print(f"[{machine_id}] 全流程完成")
    return True


# ── 并发调度（每个机体起独立子进程）──────────────────────────────

def run_in_subprocess(machine_id: str, extra_args: list[str]) -> tuple[str, bool, str]:
    """
    在独立子进程中运行单机体全流程。
    返回 (machine_id, success, output)。
    """
    cmd = [sys.executable, __file__, machine_id, "--_single"] + extra_args
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output = proc.stdout + (proc.stderr if proc.returncode != 0 else "")
    return machine_id, proc.returncode == 0, output


def run_batch_parallel(ids: list[str], extra_args: list[str], workers: int, retries: int = 2):
    results: dict[str, bool] = {}
    pending = list(ids)
    total = len(pending)
    done = 0

    print(f">>> 并发处理 {total} 个机体，workers={workers}\n")

    for attempt in range(1 + retries):
        if not pending:
            break
        if attempt > 0:
            print(f"\n>>> 第 {attempt}/{retries} 次重试，{len(pending)} 个机体")

        still_failed = []
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(run_in_subprocess, mid, extra_args): mid for mid in pending}
            for future in as_completed(futures):
                mid, ok, output = future.result()
                if attempt == 0:
                    done += 1
                with _print_lock:
                    print(f"\n{'─'*50}")
                    if attempt == 0:
                        print(f"[{done}/{total}] {mid}  {'OK' if ok else 'FAIL'}")
                    else:
                        print(f"[重试 {attempt}/{retries}] {mid}  {'OK' if ok else 'FAIL'}")
                    print(output.rstrip())
                results[mid] = ok
                if not ok:
                    still_failed.append(mid)
        pending = still_failed

    return results


# ── 入口 ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="机体数据全流程：抓取→翻译→本地化图片")
    parser.add_argument("ids", nargs="+", help="机体 ID，支持多个，例如 m13501 m12504")
    parser.add_argument("--force",       action="store_true", help="强制重新抓取和翻译")
    parser.add_argument("--skip-scrape", action="store_true", help="跳过抓取，仅翻译+本地化")
    parser.add_argument("--model",       type=str, default="gemini-2.5-flash", help="Gemini 模型（默认 gemini-2.5-flash）")
    parser.add_argument("--workers",     type=int, default=1, help="并发子进程数（默认 1，顺序执行）")
    parser.add_argument("--retries",     type=int, default=2, help="失败后最多重试次数（默认 2）")
    parser.add_argument("--_single",     action="store_true", help=argparse.SUPPRESS)  # 子进程内部标志
    args = parser.parse_args()

    # 子进程模式：直接在本进程执行单个机体
    if args._single:
        assert len(args.ids) == 1
        ok = run_single(args.ids[0], force=args.force, model=args.model, skip_scrape=args.skip_scrape)
        sys.exit(0 if ok else 1)

    # 构造传给子进程的透传参数
    extra: list[str] = []
    if args.force:        extra.append("--force")
    if args.skip_scrape:  extra.append("--skip-scrape")
    extra += ["--model", args.model]

    # 单个机体且 workers=1 → 直接在本进程跑（省去子进程开销）
    if len(args.ids) == 1 and args.workers == 1:
        ok = False
        for attempt in range(1 + args.retries):
            if attempt > 0:
                print(f"[{args.ids[0]}] 第 {attempt}/{args.retries} 次重试...")
            ok = run_single(args.ids[0], force=args.force, model=args.model, skip_scrape=args.skip_scrape)
            if ok:
                break
        sys.exit(0 if ok else 1)

    # 多机体或 workers>1 → 并发子进程
    effective_workers = min(args.workers, len(args.ids))
    results = run_batch_parallel(args.ids, extra, effective_workers, retries=args.retries)

    print(f"\n{'='*50}")
    print("汇总")
    print(f"{'='*50}")
    for mid, ok in results.items():
        print(f"  {'OK  ' if ok else 'FAIL'} {mid}")

    failed = [m for m, ok in results.items() if not ok]
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
