"""Download all remote assets from exvsdb.com to public/images/."""
import os
import sys
import time
import urllib.request
import urllib.error

BASE = 'https://exvsdb.com/wp-content/images/exvs2ib'
ROOT = os.path.join(os.path.dirname(__file__), '..', 'public', 'images')

MACHINE_DIR = os.path.join(ROOT, 'machines')
COST_DIR = os.path.join(ROOT, 'cost')
os.makedirs(MACHINE_DIR, exist_ok=True)
os.makedirs(COST_DIR, exist_ok=True)

# --- Machine IDs from machines.js ---
import re
machines_js = os.path.join(os.path.dirname(__file__), '..', 'src', 'data', 'machines.js')
with open(machines_js, encoding='utf-8') as f:
    content = f.read()
ids = re.findall(r"id: '(m\d+)'", content)
ids = sorted(set(ids))

# --- Cost images ---
costs = [1500, 2000, 2500, 3000]
cost_files = [f'cost{c}.png' for c in costs] + [f'cost{c}_off.png' for c in costs]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://exvsdb.com/',
}

def download(url, dest, label='', retries=5):
    if os.path.exists(dest):
        print(f'  [skip] {label}')
        return True
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp, open(dest, 'wb') as f:
                f.write(resp.read())
            print(f'  [ok]   {label}')
            return True
        except urllib.error.HTTPError as e:
            print(f'  [404]  {label} ({e.code})')
            return False
        except Exception as e:
            if attempt < retries:
                time.sleep(1.5 * attempt)
            else:
                print(f'  [err]  {label} ({e})')
                return False

print(f'Downloading {len(ids)} machine images...')
ok = fail = 0
for mid in ids:
    num = mid[1:]  # strip leading 'm'
    url = f'{BASE}/{num}.png'
    dest = os.path.join(MACHINE_DIR, f'{num}.png')
    if download(url, dest, f'{mid} → {num}.png'):
        ok += 1
    else:
        fail += 1
    time.sleep(0.1)

print(f'\nDownloading {len(cost_files)} cost images...')
for fname in cost_files:
    url = f'{BASE}/cost/{fname}'
    dest = os.path.join(COST_DIR, fname)
    download(url, dest, fname)
    time.sleep(0.1)

print(f'\nDone. Machine images: {ok} ok, {fail} failed.')
