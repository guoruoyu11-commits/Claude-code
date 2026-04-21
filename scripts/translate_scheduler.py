# 批量翻译所有机体页面，控制请求频率。
#
# 使用方法：
#   py translate_scheduler.py                        # 全部（跳过已有 _zh.json）
#   py translate_scheduler.py --id m12504            # 只翻译指定机体
#   py translate_scheduler.py --force               # 覆盖所有已有译文
#   py translate_scheduler.py --delay 2.0           # 放慢段间间隔

import sys
import json
import time
import argparse
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from scrape_one import load_machines, OUTPUT_DIR
from translate_one import translate_one, DEFAULT_PROMPT_FILE

FAILED_LOG = Path(__file__).parent / "public" / "data" / "translate_failed.json"


def load_failed_ids() -> list[str]:
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
    prompt_file: str | Path = DEFAULT_PROMPT_FILE,
    model_name: str = "gemini-2.0-flash",
    delay: float = 1.0,
    force: bool = False,
) -> dict:
    all_machines = load_machines()

    if machine_ids is None:
        failed_ids = load_failed_ids()
        remaining  = [mid for mid in all_machines if mid not in failed_ids]
        ordered    = failed_ids + remaining
    else:
        ordered = machine_ids

    ordered = [mid for mid in ordered if mid in all_machines]

    total   = len(ordered)
    done    = 0
    skipped = 0
    failed  = []

    print(f"共 {total} 个机体需要翻译\n")

    for i, machine_id in enumerate(ordered, 1):
        machine = all_machines[machine_id]
        print(f"[{i:3}/{total}] >> {machine_id} {machine['name']}")

        result = translate_one(
            machine_id,
            prompt_file=prompt_file,
            model_name=model_name,
            delay=delay,
            force=force,
        )

        if result is None:
            failed.append(machine_id)
            print(f"       [FAIL]")
        elif result.get("status") == "skipped":
            skipped += 1
            print(f"       -- 跳过（已存在）")
        else:
            done += 1
            print(f"       [OK]")

        # 机体间额外等待，避免连续大量请求
        if i < total and result and result.get("status") != "skipped":
            time.sleep(2.0)

    save_failed_ids(failed)

    print(f"\n{'---' * 13}")
    print(f"完成: {done}  跳过: {skipped}  失败: {len(failed)}")
    if failed:
        print(f"失败列表已保存至 {FAILED_LOG}，下次运行将优先重试")

    return {"done": done, "skipped": skipped, "failed": len(failed)}


# ─── CLI ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="批量翻译机体攻略页面")
    parser.add_argument("--id",     type=str,   action="append", default=None, help="只翻译指定机体 ID（可多次使用）")
    parser.add_argument("--prompt", type=str,   default=str(DEFAULT_PROMPT_FILE), help="提示词文件路径")
    parser.add_argument("--model",  type=str,   default="gemini-2.0-flash",       help="Gemini 模型名")
    parser.add_argument("--delay",  type=float, default=1.0,  help="段间等待秒数（默认 1.0）")
    parser.add_argument("--force",  action="store_true",      help="覆盖已有译文")
    args = parser.parse_args()

    run_batch(
        machine_ids=args.id,
        prompt_file=args.prompt,
        model_name=args.model,
        delay=args.delay,
        force=args.force,
    )


if __name__ == "__main__":
    main()
