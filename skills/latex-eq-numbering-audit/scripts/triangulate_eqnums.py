# -*- coding: utf-8 -*-
"""三路交叉验证：PaddleOCR-JSON × MinerU-md × 本项目源码模拟。

只有「两个独立 OCR 源彼此一致、却与我们的模拟不同」才判为 CONFLICT（强证据）；
两源本身不一致的判为 UNRESOLVED（须回像素取证）。

用法:
    python tools/triangulate_eqnums.py            # 全表
    python tools/triangulate_eqnums.py --strong   # 只看 CONFLICT
"""
import json
import os
import re
import sys
import collections

ROOT = os.environ.get('AIMATH_PROJECT_ROOT', os.getcwd())


def load_json_src(path):
    """_orig_struct.json → {key: [tag,...]}（tag 为 dict，取 'num'）"""
    with open(os.path.join(ROOT, path), encoding='utf-8') as f:
        d = json.load(f)
    out = collections.OrderedDict()
    for s in d['sections']:
        out.setdefault(s['key'], [])
        out[s['key']] += [t['num'] for t in s['tags']]
    return out


def load_flat(path, keys):
    """_mineru_eqseq.json（list，有 'key'+'tags'）"""
    with open(os.path.join(ROOT, path), encoding='utf-8') as f:
        d = json.load(f)
    out = collections.OrderedDict()
    for s in d:
        out.setdefault(s['key'], [])
        out[s['key']] += list(s.get('tags') or [])
    return out


def load_ours(path):
    """_ours_eqseq.json（list，扁平事件流，含 chap/sec/num）"""
    with open(os.path.join(ROOT, path), encoding='utf-8') as f:
        d = json.load(f)
    out = collections.OrderedDict()
    for s in d:
        k = '%s.%s' % (s['chap'], '0' if s['sec'] is None else s['sec'])
        out.setdefault(k, [])
        out[k].append(s['num'])
    return out


def load_layer(path):
    """_textlayer_eqseq.json（list，有 'key' + 'max'）→ {key: max}"""
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return {}
    with open(full, encoding='utf-8') as f:
        d = json.load(f)
    out = {}
    for s in d:
        k = s['key']
        out[k] = max(out.get(k, 0), s.get('max', 0))
    return out


DIGITS = re.compile(r'^\d+$')
PRIMED = re.compile(r"^\d+['\u2032\u2019]*$")          # 3'  12''  —— 带撇的阿拉伯编号
ROMAN = re.compile(r'^(?=[ivxlcdm]+$)[ivxlcdm]{1,8}$', re.I)
FW = str.maketrans('（）', '()')
JUNK = re.compile(r"[^\d'ivxlcdm]", re.I)


def clean(t):
    """全角括号 → 半角；去掉括号与杂字符。"""
    s = t.translate(FW).strip()
    s = s.strip('()').strip()
    s = JUNK.sub('', s)
    return s


def stats(tags):
    """返回 (max_arabic, n_arabic, romans)
    `3'` 属阿拉伯（带撇），**不是**罗马数字。"""
    a, r = [], []
    for t in tags:
        s = clean(t)
        if not s:
            continue
        if DIGITS.match(s):
            a.append(int(s))
        elif PRIMED.match(s):
            a.append(int(re.match(r'\d+', s).group(0)))
        elif ROMAN.match(s):
            r.append(s)
    return (max(a) if a else 0), len(a), r


def main():
    j = load_json_src('_orig_struct.json')
    m = load_flat('_mineru_eqseq.json', None)
    o = load_ours('_ours_eqseq.json')
    L = load_layer('_textlayer_eqseq.json')

    keys = sorted(set(j) | set(m) | set(o),
                  key=lambda k: (k.split('.')[0], int(k.split('.')[1])))
    rows = []
    for k in keys:
        jm, jn, jr = stats(j.get(k, []))
        mm, mn, mr = stats(m.get(k, []))
        om, on, orr = stats(o.get(k, []))
        lm = L.get(k, 0)                     # 原书文字层最大阿拉伯编号

        # 四源表决：JSON / MinerU / 原书文字层
        votes = {'json': jm, 'mineru': mm, 'layer': lm}
        votes = {a: b for a, b in votes.items() if b > 0}
        agree = [a for a, b in votes.items() if b == om]
        differ = [a for a, b in votes.items() if b != om]
        if not votes:
            verdict = 'ours-only' if om else 'n/a'
        elif not differ:
            verdict = 'agree'
        elif not agree and len(set(votes[a] for a in differ)) == 1:
            verdict = 'CONFLICT'             # 所有有数据的源一致反对我们
        elif votes.get('layer') == om:
            verdict = 'layer-ok'             # 原书文字层确认我们
        elif 'layer' in votes:
            verdict = 'layer-diff'           # 文字层反对我们 → 需人工核
        else:
            verdict = 'unresolved'
        rows.append({'key': k, 'json': jm, 'mineru': mm, 'layer': lm, 'ours': om,
                     'json_n': jn, 'mineru_n': mn, 'ours_n': on,
                     'romans': sorted(set(jr) | set(mr)), 'verdict': verdict})

    order = ['CONFLICT', 'layer-diff', 'unresolved', 'layer-ok', 'ours-only',
             'agree', 'n/a']
    buckets = collections.OrderedDict((v, []) for v in order)
    other = []
    for r in rows:
        (buckets[r['verdict']] if r['verdict'] in buckets else other).append(r)

    def show(title, rs):
        print('===== %s (%d) =====' % (title, len(rs)))
        if not rs:
            print('  (none)')
            print()
            return
        print('  %-9s %6s %7s %6s %6s   %s' %
              ('key', 'JSON', 'MinerU', 'LAYER', 'OURS', 'delta(JSON-OURS)'))
        for r in rs:
            d = r['json'] - r['ours']
            print('  %-9s %6s %7s %6s %6s   %+d' %
                  (r['key'], r['json'], r['mineru'], r['layer'], r['ours'], d))
        print()

    show('CONFLICT  (所有有数据的源一致反对我们)', buckets['CONFLICT'])
    show('layer-diff (文字层反对我们 → 须人工核)', buckets['layer-diff'])
    show('unresolved (无文字层数据且其他源不一致)', buckets['unresolved'])
    if '--strong' not in sys.argv:
        show('layer-ok  (文字层确认我们，其他源噪声)', buckets['layer-ok'])
        show('agree', buckets['agree'])
        show('n/a / ours-only', buckets['n/a'] + buckets['ours-only'])

    with open(os.path.join(ROOT, '_eq_triangulate.json'), 'w',
              encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
