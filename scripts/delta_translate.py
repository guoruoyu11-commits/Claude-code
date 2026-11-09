# 增量翻译工具：diff 旧/新 wiki 数据 → 旧译文精确复用 + 术语/连段自动层 → 仅导出新增文段待翻
#
# 设计（编号确定性）：
#   extract 时对短语本做快照存盘；apply 必须用同一快照回放过滤顺序，
#   保证 gid（页内第 N 个残余文段）在 extract/apply 两侧完全一致。
#   ※ 修改 auto_rules 的 token/规则后必须重新 extract，否则编号错位。
#
# 用法：
#   python3 scripts/delta_translate.py extract  # 统计+导出待翻片段 → workdir/pending_*.json
#   python3 scripts/delta_translate.py status   # 查看各机体覆盖进度
#   python3 scripts/delta_translate.py apply    # 对译文完整的机体：生成新 _zh 并换入新数据
#   可选环境变量: STAGING=/tmp/machines_staging WORKDIR=/tmp/retrans
import sys, json, copy, os
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

BASE = Path(__file__).parent.parent
OUT_DIR = BASE / 'public' / 'data' / 'machines'
STAGING = Path(os.environ.get('STAGING', '/tmp/machines_staging'))
WORKDIR = Path(os.environ.get('WORKDIR', '/tmp/retrans'))
sys.path.insert(0, str(WORKDIR))
sys.path.insert(0, str(Path(__file__).parent))  # 优先仓库内 auto_rules

from html_to_nodes import html_to_nodes
from ja_zh_dict import apply_dict
from translate_nodes import collect_refs, _build_output
try:
    from scripts.auto_rules import auto_translate, build_norm_book, norm_lookup  # noqa
except ImportError:
    from auto_rules import auto_translate, build_norm_book, norm_lookup  # noqa

MODEL = 'manual-glm'
KANA = __import__('re').compile(r'[぀-ゖァ-ヺ]')  # 假名检测（不含中点・与长音符ー）


def load_book():
    """短语本 = 全部 _zh 翻译日志的 原文→译文 映射"""
    book = {}
    for p in OUT_DIR.glob('*_zh.json'):
        try:
            log = json.loads(p.read_text(encoding='utf-8')).get('translation_log', [])
        except Exception:
            continue
        for e in log:
            s, t = e.get('source'), e.get('target')
            if s and t and s not in book:
                book[s] = t
    return book


def collect_pages():
    """[(page_id, staging_path), ...] 依据 diff 报告"""
    report = json.loads((WORKDIR / 'diff_report.json').read_text(encoding='utf-8'))
    pages = []
    for mid, info in sorted(report['changed'].items()):
        pages.append((mid, STAGING / f'{mid}.json'))
        for s in info.get('subs', []):
            pages.append((s, STAGING / f'{s}.json'))
    return pages


def load_nodes(page_id: str) -> dict:
    """读 staging 页面（带节点缓存），返回 src dict"""
    sp = STAGING / f'{page_id}.json'
    src = json.loads(sp.read_text(encoding='utf-8'))
    if 'content_nodes' not in src:
        src['content_nodes'] = html_to_nodes(src.get('content_html', ''))
        sp.write_text(json.dumps(src, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    return src


def filter_refs(nodes, book, norm_book):
    """按 extract 顺序过滤：book → 归一化 book → 字典 → 自动规则；返回 (dict_log, pending_refs)"""
    dict_log, pending, book_hits = [], [], 0
    all_refs = []
    collect_refs(nodes, all_refs)
    for ref in all_refs:
        v = ref['node'][ref['key']]
        if v in book:
            ref['node'][ref['key']] = book[v]
            book_hits += 1
            continue
        nt = norm_lookup(v, norm_book)
        if nt is not None and not KANA.search(nt):
            ref['node'][ref['key']] = nt
            dict_log.append({'source': v, 'target': nt, 'method': 'norm', 'node_type': ref['node'].get('t', '#')})
            continue
        t, hit = apply_dict(v)
        if hit:
            ref['node'][ref['key']] = t
            dict_log.append({'source': v, 'target': t, 'method': 'dict', 'node_type': ref['node'].get('t', '#')})
            continue
        t, mode = auto_translate(v)
        if mode and not KANA.search(t):
            ref['node'][ref['key']] = t
            dict_log.append({'source': v, 'target': t, 'method': mode, 'node_type': ref['node'].get('t', '#')})
            continue
        pending.append(ref)
    return book_hits, dict_log, pending


def cmd_extract():
    book = load_book()
    norm_book = build_norm_book(book)
    (WORKDIR / 'book_snapshot.json').write_text(json.dumps(book, ensure_ascii=False), encoding='utf-8')
    (WORKDIR / 'norm_book_snapshot.json').write_text(json.dumps(norm_book, ensure_ascii=False), encoding='utf-8')

    segments, manifest = {}, {}
    stats = {'reuse': 0, 'auto': 0, 'pending': 0, 'chars': 0}
    for page_id, _ in collect_pages():
        src = load_nodes(page_id)
        nodes = copy.deepcopy(src['content_nodes'])
        book_hits, dict_log, pending = filter_refs(nodes, book, norm_book)
        stats['reuse'] += book_hits
        stats['auto'] += sum(1 for e in dict_log if e['method'] in ('norm', 'combo', 'ext'))
        for n, ref in enumerate(pending):
            segments[f'{page_id}#{n}'] = ref['node'][ref['key']]
        manifest[page_id] = {'pending': len(pending)}
        stats['pending'] += len(pending)
        stats['chars'] += sum(len(r['node'][r['key']]) for r in pending)

    (WORKDIR / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding='utf-8')
    # 按机体分组输出（翻完一台即可 apply 一台）
    by_machine = {}
    for gid, t in sorted(segments.items()):
        mid = gid.split('#')[0].split('_p')[0]
        by_machine.setdefault(mid, []).append({'gid': gid, 't': t})
    for f in sorted(WORKDIR.glob('pending_*.json')):
        f.unlink()
    n_files = 0
    for mid, items in sorted(by_machine.items()):
        (WORKDIR / f'pending_{mid}.json').write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding='utf-8')
        n_files += 1

    print(f"复用 {stats['reuse']} + 自动 {stats['auto']} + 待翻 {stats['pending']} 段 / {stats['chars']} 字符")
    print(f"待翻片段按机体分 {n_files} 个文件 → {WORKDIR}/pending_m*.json")
    done_machines = sorted({pid.split('#')[0].split('_p')[0] for pid in segments} - set())  # noqa
    full = [pid for pid, m in manifest.items() if m['pending'] == 0]
    print(f"零残余页面（可直接 apply）: {len(full)}")


def load_translations():
    trans = {}
    for f in sorted(WORKDIR.glob('done_*.json')):
        trans.update(json.loads(f.read_text(encoding='utf-8')))
    return trans


def cmd_status():
    trans = load_translations()
    manifest = json.loads((WORKDIR / 'manifest.json').read_text(encoding='utf-8'))
    pages = manifest.keys()
    remaining_pages = {}
    covered = partial = 0
    for page_id in pages:
        need = manifest[page_id]['pending']
        if need == 0:
            covered += 1
            continue
        have = sum(1 for n in range(need) if f'{page_id}#{n}' in trans)
        if have >= need:
            covered += 1
        else:
            partial += 1
            remaining_pages[page_id] = need - have
    # 按机体聚合
    per_machine = {}
    for page_id, miss in remaining_pages.items():
        mid = page_id.split('_p')[0]
        per_machine[mid] = per_machine.get(mid, 0) + miss
    total_miss = sum(per_machine.values())
    print(f'页面: {covered} 页译文齐备 / {partial} 页未齐 (缺 {total_miss} 段)')
    print('未齐机体 Top15:')
    for mid, miss in sorted(per_machine.items(), key=lambda kv: -kv[1])[:15]:
        print(f'  {mid}: 缺 {miss} 段')


def cmd_apply():
    trans = load_translations()
    manifest = json.loads((WORKDIR / 'manifest.json').read_text(encoding='utf-8'))
    book = json.loads((WORKDIR / 'book_snapshot.json').read_text(encoding='utf-8'))
    norm_book = json.loads((WORKDIR / 'norm_book_snapshot.json').read_text(encoding='utf-8'))

    applied, skipped = [], []
    for page_id, _ in collect_pages():
        need = manifest[page_id]['pending']
        have = all(f'{page_id}#{n}' in trans for n in range(need))
        if not have:
            skipped.append(page_id)
            continue
        src = load_nodes(page_id)
        nodes = copy.deepcopy(src['content_nodes'])
        book_hits, dict_log, pending = filter_refs(nodes, book, norm_book)
        log = []
        for n, ref in enumerate(pending):
            gid = f'{page_id}#{n}'
            original = ref['node'][ref['key']]
            ref['node'][ref['key']] = trans[gid]
            log.append({'source': original, 'target': trans[gid], 'method': 'manual', 'node_type': ref['node'].get('t', '#')})
        # 写 _zh（staging 数据原样换入 live）
        data = _build_output(page_id, src, nodes, MODEL, translation_log=dict_log + log)
        (OUT_DIR / f'{page_id}_zh.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        (OUT_DIR / f'{page_id}.json').write_text(
            json.dumps(src, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
        applied.append(page_id)
    mids = sorted({p.split('_p')[0] for p in applied})
    print(f'已接入 {len(applied)} 页 / {len(mids)} 台机体: {" ".join(mids) if mids else "无"}')
    if skipped:
        print(f'跳过（译文未齐）{len(skipped)} 页')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    {'extract': cmd_extract, 'status': cmd_status, 'apply': cmd_apply}[cmd]()
