import re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('view-source_https___exvsdb.com_exvs2ib_rank_.html', 'r', encoding='utf-8') as f:
    html = f.read()

tier_map = {
    'S': 'S', 'Ap': 'A+', 'A': 'A', 'Am': 'A-',
    'Bp': 'B+', 'B': 'B', 'Bm': 'B-', 'C': 'C', 'Z': 'Z'
}

machines = []
pattern = re.compile(r'<td id="cost(\d+)List(\w+)">(.*?)(?=</td></tr>)', re.DOTALL)
img_pattern = re.compile(r'<img src="(https://exvsdb\.com/wp-content/images/exvs2ib/(\d+)\.png)"[^>]*alt="([^"]+)"')

for m in pattern.finditer(html):
    cost = int(m.group(1))
    tier_key = m.group(2)
    content = m.group(3)
    tier = tier_map.get(tier_key, tier_key)
    for img_m in img_pattern.finditer(content):
        img_url = img_m.group(1)
        id_num = img_m.group(2)
        name = img_m.group(3)
        machines.append({'id_num': id_num, 'name': name, 'cost': cost, 'tier': tier, 'img': img_url})

def make_short(name):
    short = re.sub(r'[（(][^）)]*[）)]', '', name).strip()
    short = re.sub(r'\s+', '', short)
    if len(short) > 6:
        short = short[:6]
    return short

lines = []
lines.append('export const MACHINES = [')

costs = [3000, 2500, 2000, 1500]
tiers_order = ['S', 'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C', 'Z']

for cost in costs:
    lines.append(f'  // ══════════ {cost} COST ══════════')
    for tier in tiers_order:
        group = [m for m in machines if m['cost'] == cost and m['tier'] == tier]
        if not group:
            continue
        lines.append(f'  // {tier}')
        for m in group:
            mid = f"m{m['id_num']}"
            name_escaped = m['name'].replace("'", "\\'")
            short = make_short(m['name'])
            img = m['img']
            lines.append(f"  {{ id: '{mid}', name: '{name_escaped}', short: '{short}', cost: {m['cost']}, tier: '{m['tier']}', img: '{img}' }},")

lines.append(']')
lines.append('')
lines.append("export const TIERS = ['S', 'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C']")
lines.append('')
lines.append('export const TIER_META = {')
lines.append("  'S':  { label: 'S',  sub: '最強',   cls: 's'     },")
lines.append("  'A+': { label: 'A+', sub: '',        cls: 'aplus'  },")
lines.append("  'A':  { label: 'A',  sub: '',        cls: 'a'      },")
lines.append("  'A-': { label: 'A-', sub: '',        cls: 'aminus' },")
lines.append("  'B+': { label: 'B+', sub: '',        cls: 'bplus'  },")
lines.append("  'B':  { label: 'B',  sub: '',        cls: 'b'      },")
lines.append("  'B-': { label: 'B-', sub: '',        cls: 'bminus' },")
lines.append("  'C':  { label: 'C',  sub: '要強化',  cls: 'c'      },")
lines.append('}')

output = '\n'.join(lines)
with open('src/data/machines.js', 'w', encoding='utf-8') as f:
    f.write(output)

print(f"Done! {len(machines)} machines written to machines.js")
