import glob
import os
import shutil
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'DiffSinger', 'checkpoints', 'lightning_logs', 'latest')
VIEWS = os.path.join(ROOT, 'DiffSinger', 'tb_views')


def classify(path):
    c_var = c_mel = 0
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(8 << 20)
            if not chunk:
                break
            c_var += chunk.count(b'var_loss')
            c_mel += chunk.count(b'mel_loss')
    if c_var > 0:
        return 'variance'
    if c_mel > 0:
        return 'acoustic'
    return 'unknown'


def run_name(base):
    try:
        ts = base.split('.')[3]
        return time.strftime('%Y%m%d_%H%M%S', time.localtime(int(ts)))
    except Exception:
        return base


def build_view(kind):
    view = os.path.join(VIEWS, kind)
    shutil.rmtree(view, ignore_errors=True)
    os.makedirs(view, exist_ok=True)

    files = sorted(glob.glob(os.path.join(SRC, 'events.out.*')))
    n = 0
    used = set()
    for f in files:
        if classify(f) != kind:
            continue
        base = os.path.basename(f)
        name = run_name(base)
        if name in used:
            i = 2
            while f'{name}_{i}' in used:
                i += 1
            name = f'{name}_{i}'
        used.add(name)
        sub = os.path.join(view, name)
        os.makedirs(sub, exist_ok=True)
        dst = os.path.join(sub, base)
        try:
            os.link(f, dst)
        except OSError:
            shutil.copy2(f, dst)
        n += 1
        print(f'  {kind}: {name} ({os.path.getsize(f) / 1e6:.1f} MB)')

    print(f'View ready: {view} ({n} run(s))')
    if n == 0:
        print('WARNING: no matching event files found.')


if __name__ == '__main__':
    kind = sys.argv[1] if len(sys.argv) > 1 else 'variance'
    if kind not in ('variance', 'acoustic'):
        sys.exit('usage: make_tb_views.py variance|acoustic')
    build_view(kind)