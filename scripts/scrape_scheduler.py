# 批量抓取所有机体页面，控制请求频率。
#
# 使用方法：
#   py scrape_scheduler.py                   # 全部（跳过已存在）
#   py scrape_scheduler.py --delay 2.0       # 放慢到 2 秒/次
#   py scrape_scheduler.py --id m12504       # 只抓指定机体
#   py scrape_scheduler.py --force           # 覆盖所有已有文件
#   py scrape_scheduler.py --debug           # 调试第一个页面

import sys
import json
import time
import argparse
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from scrape_one import scrape_one, load_machines, close_browser, OUTPUT_DIR

FAILED_LOG = Path(__file__).parent.parent / "public" / "data" / "failed.json"


def load_failed_ids() -> list[str]:
    """读取上次失败的机体 ID 列表，优先重试。"""
    if FAILED_LOG.exists():
        try:
            return json.loads(FAILED_LOG.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def save_failed_ids(ids: list[str]):
    FAILED_LOG.parent.mkdir(parents=True, exist_ok=True)
    FAILED_LOG.write_text(json.dumps(ids, ensure_ascii=False), encoding="utf-8")


def run_batch(
    machine_ids: list[str] | None = None,
    delay: float = 0.8,
    force: bool = False,
    debug: bool = False,
) -> dict:
    """
    按频率依次调用 scrape_one()。

    参数：
      machine_ids — 要处理的 ID 列表；None 表示全部
      delay       — 每次请求后等待的秒数
      force       — 是否覆盖已有文件
      debug       — 调试模式：只处理第一个，打印 HTML 骨架

    返回：{done, skipped, failed}
    """
    all_machines = load_machines()

    if machine_ids is None:
        # 优先处理上次失败的，再处理其余
        failed_ids = load_failed_ids()
        remaining  = [mid for mid in all_machines if mid not in failed_ids]
        ordered    = failed_ids + remaining
    else:
        ordered = machine_ids

    # 过滤掉 machines.js 中不存在的 ID
    ordered = [mid for mid in ordered if mid in all_machines]

    total   = len(ordered)
    done    = 0
    skipped = 0
    failed  = []

    print(f"共 {total} 个机体需要处理  (delay={delay}s)\n")

    for i, machine_id in enumerate(ordered, 1):
        machine = all_machines[machine_id]
        print(f"[{i:3}/{total}] >> {machine_id} {machine['name']}")

        result = scrape_one(machine_id, force=force, debug=debug)

        if debug:
            print("\n[调试模式] 只处理第一个，退出。")
            break

        if result is None:
            failed.append(machine_id)
            print(f"       [FAIL]")
        elif result.get("status") == "skipped":
            skipped += 1
            print(f"       -- 跳过（已存在）")
        else:
            done += 1
            print(f"       [OK]")

        if i < total:
            time.sleep(delay)

    # 保存失败列表供下次优先重试
    save_failed_ids(failed)
    close_browser()

    print(f"\n{'---' * 13}")
    print(f"完成: {done}  跳过: {skipped}  失败: {len(failed)}")
    if failed:
        print(f"失败列表已保存至 {FAILED_LOG}，下次运行将优先重试")
    print(f"数据保存至: {OUTPUT_DIR}")

    return {"done": done, "skipped": skipped, "failed": len(failed)}


# ─── CLI ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="批量抓取机体攻略页面（频率控制）")
    parser.add_argument("--delay", type=float, default=0.8, help="请求间隔秒数（默认 0.8）")
    parser.add_argument("--id",    type=str,   default=None, help="只抓取指定机体 ID")
    parser.add_argument("--force", action="store_true",     help="覆盖已有文件")
    parser.add_argument("--debug", action="store_true",     help="调试第一个页面")
    args = parser.parse_args()

    ids = [args.id] if args.id else None
    run_batch(machine_ids=ids, delay=args.delay, force=args.force, debug=args.debug)


if __name__ == "__main__":
    main()
