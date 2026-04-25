"""
Replace atwiki image URLs in machine JSON files with local /images/machines/{num}.png
"""
import re
import json
import sys
from pathlib import Path

BASE_DIR   = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "public" / "data" / "machines"

# Matches both protocol-relative (//img.atwiki.jp/...) and https:// variants
ATWIKI_IMG = re.compile(r'(?:https?:)?//img\.atwiki\.jp/[^\s"\'\\]+')


def machine_num(json_path: Path) -> str:
    """Extract numeric part from filename: m12504.json -> '12504', m24501_p108.json -> '24501'"""
    stem = json_path.stem          # e.g. m12504 or m24501_p108 or m12504_zh
    base = stem.split('_')[0]      # m12504
    return base.lstrip('m')        # 12504


def process_file(path: Path) -> int:
    text = path.read_text(encoding='utf-8')
    num = machine_num(path)
    local_url = f'/images/machines/{num}.png'

    updated, count = ATWIKI_IMG.subn(local_url, text)
    if count:
        path.write_text(updated, encoding='utf-8')
    return count


def main():
    files = sorted(OUTPUT_DIR.glob('*.json'))
    total = 0
    for f in files:
        count = process_file(f)
        if count:
            print(f'  [ok] {f.name}: replaced {count} URL(s) -> /images/machines/{machine_num(f)}.png')
        total += count
    print(f'\nDone. {total} URL(s) replaced across {len(files)} files.')


if __name__ == '__main__':
    main()
