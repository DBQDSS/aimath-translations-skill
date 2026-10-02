# -*- coding: utf-8 -*-
"""第四路独立源：原书 PDF 自带文字层里的右缘“方程编号”标签。

与前三个源（PaddleOCR-JSON / MinerU-md / 本项目源码模拟）相互独立：
文字层由扫描 PDF 的 OCR 生成，位置精确，能捕捉到 JSON 漏标的 tag
（例如 VIII.5 的 (3)(4) 写在散文行右缘、XIII.2 的 (3)(28) 同理）。

关键难点是“起始页污染”：一节往往在上一节的末页中缝起排，该页右缘
同时含上一节尾部标签（大号）与本节首个 (1)。本工具按**全局读数流**处理：
把全书右缘标签按 (page, y) 排序，遇到某节的起始页时，以该页上**第一个
阿拉伯 (1)** 为分界——之前的归上一节，之后的归本节。这样无需知道标题
的 y 坐标即可正确切分。

用法:
    python tools/textlayer_eqseq.py                 # 全表：逐节对比 + 写 JSON
    python tools/textlayer_eqseq.py VIII.5          # 单节明细（逐页右缘标签）
    python tools/textlayer_eqseq.py --json          # 仅重生成 _textlayer_eqseq.json
"""
import json
import os
import re
import sys
import collections

import pymupdf

ORIG = r'F:\大学\数字资源\数学\分析学\泛函分析\吉田耕作\functional analysis Yosida.pdf'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLIO_OFFSET = 16          # folio = pdf_index - 16  (与 render_orig_strip 一致)
X_MIN = 352.0              # 右缘起点（版心右界约 373pt）
OUT_JSON = '_textlayer_eqseq.json'

# 形如 (12)  (12')  (12'')  (i)  (vii')  —— 必须带括号；
# 收尾允许 ) ] } （OCR 常把右括号认成 } 或 ]）
TAG = re.compile(r"^\((\d{1,3}|[ivxlcdmIVXLCDM]{1,6})"
                 r"(['\u2032\u2033\u2019\u201d\x22]{0,3})[)\]}][.,]?$")
ROMAN = re.compile(r'^[ivxlcdm]+$')
GAP_MIN = 8.0              # 真编号与左侧内容的水平空隙下限（pt）：
                           # “Thus, by (1)”这类行末交叉引用紧贴正文，会被剔除


def normalize(raw):
    """(I)" -> (1)″ 那样把 OCR 把 1 认成 I 的情形归一；返回 (value, np)
    value: int（阿拉伯）或小写罗马串；np: 撇号个数。"""
    m = TAG.match(raw.replace(' ', ''))
    if not m:
        return None
    body, primes = m.group(1), m.group(2)
    np_ = len(primes)
    if body.isdigit():
        return int(body), np_
    if ROMAN.match(body):
        return body, np_
    up = body.upper()
    if up == 'I':
        return 1, np_
    return up.lower(), np_


def page_tags(pg):
    """返回该页右缘的编号标签（按 y 从上到下）。

    只保留“真编号”：位于右缘、且与其同一行左侧内容之间有足够空隙
    （GAP_MIN）的 token。这样可剔除行末的交叉引用，如 “Thus, by (1)”。
    """
    words = [w for w in pg.get_text('words')
             if 60 < w[1] < pg.rect.height - 40]
    # 按行（y）分组
    words.sort(key=lambda w: (round(w[1] / 3.0), w[0]))
    lines = []
    for w in words:
        if lines and abs(lines[-1][0][1] - w[1]) < 4:
            lines[-1].append(w)
        else:
            lines.append([w])
    out = []
    for ln in lines:
        ln.sort(key=lambda w: w[0])
        for i, w in enumerate(ln):
            x0, y0, txt = w[0], w[1], w[4]
            if x0 < X_MIN or len(txt) > 7:
                continue
            v = normalize(txt)
            if v is None:
                continue
            if i > 0:
                prev_x1 = ln[i - 1][2]        # 左邻 token 的右边界
                if (x0 - prev_x1) < GAP_MIN:  # 紧贴正文 → 交叉引用
                    continue
            out.append({'y': round(y0, 1), 'raw': txt, 'val': v[0], 'np': v[1]})
    out.sort(key=lambda d: d['y'])
    return out


def section_bounds(secs):
    """每节 [start, end) 页码区间（end = 下一节/章起始页，独占）。"""
    bounds = []
    for i, s in enumerate(secs):
        end = None
        for s2 in secs[i + 1:]:
            if s2['kind'] in ('chapter', 'section'):
                end = s2['start_page']
                break
        bounds.append((s['key'], s['start_page'], end))
    return bounds


def build_assignment(doc, secs):
    """全局读数流 → {key: [tags]}，按起始页首个 (1) 切分，避免起始页污染。"""
    # 起始页 → key（同一页有多个起始时，section 优先于 intro）
    start_map = collections.OrderedDict()
    for s in secs:
        p = s['start_page']
        if p not in start_map or s['kind'] in ('chapter', 'section'):
            if start_map.get(p) is None or s['kind'] in ('chapter', 'section'):
                start_map[p] = s['key']
    # 若同页有多个 chapter/section（罕见），取 sec 最小者作为切分锚点
    n = len(doc)
    per_key = collections.defaultdict(list)
    cur = None
    for pi in range(n):
        tags = page_tags(doc[pi])
        if not tags:
            if pi in start_map:
                cur = start_map[pi]
            continue
        if pi in start_map:
            k = start_map[pi]
            # 找该页上第一个阿拉伯 (1)
            split = None
            for j, t in enumerate(tags):
                if t['val'] == 1 and t['np'] == 0:
                    split = j
                    break
            if split is None:
                # 该节首式不在本页：本页 tags 归上一节，切换锚点后继续
                if cur:
                    per_key[cur] += tags
            else:
                if cur:
                    per_key[cur] += tags[:split]
                per_key[k] += tags[split:]
            cur = k
        else:
            if cur:
                per_key[cur] += tags
    return per_key


def per_key_max(tags):
    """(max阿拉伯编号, 阿拉伯个数, 罗马集合)。"""
    arab, rom = [], set()
    for t in tags:
        if isinstance(t['val'], int):
            arab.append(t['val'])
        else:
            rom.add(t['val'])
    return (max(arab) if arab else 0), len(arab), sorted(rom)


def ours_map():
    with open(os.path.join(ROOT, '_ours_eqseq.json'), encoding='utf-8') as f:
        d = json.load(f)
    out = collections.defaultdict(list)
    for e in d:
        k = '%s.%s' % (e['chap'], '0' if e['sec'] is None else e['sec'])
        out[k].append(e['num'])
    return out


def load_struct():
    with open(os.path.join(ROOT, '_orig_struct.json'), encoding='utf-8') as f:
        return json.load(f)


def single(key):
    st = load_struct()
    secs = st['sections']
    doc = pymupdf.open(ORIG)
    per_key = build_assignment(doc, secs)
    got = per_key.get(key, [])
    print('===== %s  文字层右缘标签（读数流） =====' % key)
    print('  max=%s  tags=%s' %
          (per_key_max(got)[0], ' '.join(str(t['val']) for t in got)))
    o = ours_map().get(key, [])
    nums = [int(x) for x in o if x.isdigit()]
    print('  ours max=%s' % (max(nums) if nums else 0))
    print()
    # 逐页
    sec = next((s for s in secs if s['key'] == key), None)
    if sec:
        for pi in range(sec['start_page'], sec['start_page'] + 6):
            tg = page_tags(doc[pi])
            print('  idx %d (folio %s): %s' % (pi, pi - FOLIO_OFFSET,
                  ' '.join(t['raw'] for t in tg) or '(none)'))


def main():
    st = load_struct()
    secs = st['sections']
    doc = pymupdf.open(ORIG)
    per_key = build_assignment(doc, secs)
    ours = ours_map()

    rows = []
    print('%-10s %6s %6s %6s   %s' % ('key', 'LAYER', 'OURS', 'diff', 'tags'))
    seen = set()
    for key, a, b in section_bounds(secs):
        if key in seen:
            continue
        seen.add(key)
        got = per_key.get(key, [])
        mx, na, rom = per_key_max(got)
        mine = [int(x) for x in ours.get(key, []) if x.isdigit()]
        omx = max(mine) if mine else 0
        seq = [str(t['val']) for t in got]
        flag = '' if mx == omx else '  <<<'
        print('%-10s %6s %6s %6s   %s%s' % (key, mx, omx, mx - omx,
              ' '.join(seq[:30]), flag))
        rows.append({'key': key, 'max': mx, 'n': na, 'romans': rom,
                     'ours': omx, 'tags': seq})

    with open(os.path.join(ROOT, OUT_JSON), 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)

    mm = [r for r in rows if r['max'] != r['ours']]
    print()
    print('mismatch sections: %d / %d' % (len(mm), len(rows)))
    for r in mm:
        print('   %-9s LAYER=%-3s OURS=%-3s' % (r['key'], r['max'], r['ours']))


if __name__ == '__main__':
    if '--json' in sys.argv:
        main()
    elif len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        single(sys.argv[1])
    else:
        main()
