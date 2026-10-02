---
name: math-pdf-bookmark
description: >-
  Add precise, clickable bookmarks (jumping to the heading's y-coordinate, not the
  page top) to a large folder of math PDFs. Handles two populations: text-layer PDFs
  whose table of contents must be parsed from span geometry, and pure-scanned PDFs
  that first need an invisible OCR text layer. Proven across 数论 / 拓扑 / 代数学 /
  分析学 (1000+ PDFs). Use whenever a user says "给某文件夹的 PDF 加书签" / "加目录"
  / "bookmark these PDFs".
---

# math-pdf-bookmark — 数学 PDF 批量精确书签

## When to use
- User wants bookmarks / 目录 / 书签 on a folder of math PDFs.
- Requirement (from this user): bookmarks must jump to the **heading's y position**,
  not the top of the printed page. This is the single hardest correctness constraint.

## Hard rules (non-negotiable)
1. `set_toc` 第 4 字段（destination）必须是**数字**（距页顶磅数 `top`），不能是 dict，否则链接失效。
2. 定位失败 / 偏移算错的条目**一律丢弃**，绝不退化成 `p=cursor` 兜底——那会指向错误页。
3. 匹配必须用**词元重合率**（`toks()` + `overlap()`），不能用精确子串，也不能从 `norm()` 结果分词
   （`norm()` 删空格会把英文标题压成超长"单词"，重合率恒 0）。
4. 单进程串行跑书签生成；OCR 至多 2 路。开 6+ 并行进程会**跑死机**。

## Pipeline (per folder, e.g. `F:/.../分析学`)
工作目录 `_build/`，脚本：`tlbmk.py`(解析引擎) `build_t1.py`(书签生成) `diag.py`(分类)
`verify.py`(全库校验) `probe_t1.py` `worklist.py` `recover_empties.py`；
OCR 相关：`wocr_all.py`(多 worker) `winocr.ps1`(WinRT) `render_pages.py` `wocr_build.py`(不可见文字层)
`copyback.py`；图像目录书专用：`inject_imagetoc.py`(前台 OCR 注入) `build_imagetoc2.py`(标题式抽取)。

**复用纪律（复制到新文件夹后必须重指路径）**：
- `diag.py`、`worklist.py`、`verify.py` 硬编码 `ROOT`（各自文件顶部）→ 改 `ROOT="F:/.../新文件夹"`。
- `wocr_all.py`、`copyback.py` 硬编码 `BUILD` → 改 `BUILD="F:/.../新文件夹/_build"`。
- `build_t1.py`/`tlbmk.py`/`recover_empties.py` **不依赖 ROOT**（走 worklist，路径由 worklist 提供），无需改。
- ⚠️ `verify.py` 的 `ROOT` 极易漏改：漏改会扫描到旧文件夹而误报/漏报，务必每个新文件夹都核对一遍。

### Phase 0 — 分类 (diag.py)
对每本 PDF 取文本层，按前 11 个分位采样文字密度：
- A-ok：已有合格书签（跳过）
- T1：有文字层、无书签 → 直接进入 Phase 2
- S1：纯扫描件（密度 < 50%）→ Phase 1 OCR 后并入 T1 管线
扫描件末页常有元数据文字骗过密度采样 → 必须**多分位采样**，否则误判 T1。

### Phase 1 — S1 扫描件 OCR（不可见文字层）
复用 `pdf-scanned-ocr-bookmark` skill 的 WinRT OCR 流程（Windows.Media.Ocr, zh-Hans-CN），
`winocr.ps1` 按原生 DPI 渲染、`wocr_all.py` 多 worker、`copyback.py` 把文字层 `saveIncr` 回拷原文件。
OCR 噪声大 → 后续 Phase 2 目录检测要用宽松模式。

### Phase 1b — 目录页是图片、但正文有文字层（"图像目录书"，如 Ahlfors/Courant/林源渠）
正文能定位、只有目录页是扫描图 → 不必全本 OCR。轻量做法（实测有效）：
1. `inject_imagetoc.py <pdf>`：只 OCR 前台 ~60 页（`render_pages.py`+`winocr.ps1`），
   用 `is_toc_line` 找出连续 TOC 页，把那段 OCR 文字以 `render_mode=3` 不可见层
   注入**原文件对应页**（`wocr_build.py` 写临时 pdf 后 `shutil.copyfile` 回拷，按页数对校验）。
2. 先试 `build_t1.build_one`（标准行式解析）；若返回 None/很少，用
   `build_imagetoc2.py`：**标题式抽取**——从注入的 TOC 文字抓
   `第X章 / Chapter N / §N / 附录 / Part N / Volume N` 等标题，再到正文文字层
   `overlap>=0.62` 定位 (page,y) 写书签。
   这类书目录是"左栏章节名 + 右栏页码列"两栏布局，行式解析器配不上，必须用标题式。
   结果：Ahlfors 23 / Courant 26 / 林源渠 21 条，均跳转到标题 y。

### Phase 2 — T1 / S1 书签生成 (build_t1.py)
核心函数 `build_one(path)`：
1. `find_toc_pages(doc)` 定位目录页（连续"左标题+右页码"行 run + 锚点验证）。
   严格检测 < 4 条时自动 `find_toc_pages_loose` 重试（容忍 OCR 噪声）。
2. `parse_toc` 用 **span 级 y 聚类**重建行（目录行常被拆成 序号/标题/页码 三个 span，
   且有重复 span 需去重），点线正则要求**至少两个点字符**。
3. `assign_levels` 按缩进定层级。
4. `locate` 解析每条到 (物理页, y)：
   - 先试印刷页偏移 `offset`（由页眉页码图 `header_pagemap` 推出，必须 `validate_offset` 抽样验证）；
   - 偏移不可靠则 `fit_offset`（定位前 ~16 条标题反推模态偏移）；
   - 仍无则**正文逐页搜索标题词元**（`overlap >= 0.72`），连续 10 条失败即截断（防"第二/三册"清单）。
5. `apply_toc` 写 `set_toc`，强制层级 + 页码单调（`p = max(cursor, min(p, n-1))`）。
   - 质量闸门：条目塌缩到 < 3 页 → REJECT（不写）；这比写垃圾书签好。

### Phase 3 — 校验 + 找回 (verify.py / recover_empties.py)
- `verify.py` 全库走一遍：统计总书签数、unopenable / out-of-range / non-monotonic / dead-dests。
  **本管线产出的书必须 0 上述异常**；既有 PDF 原有的脏书签不在范围内（报告即可）。
- 对全部 0 书签 PDF 跑 `recover_empties.py`（调用 `build_one`）：
  既恢复"日志记了但写入丢失"的书，又补回被严格检测误杀的教科书；真正无目录的书
  （答案是/勘误/单章习题卷/短论文/公式集）会自然 skip。

## Critical gotchas (tlbmk.py)
- `_split_page_number`：对**单 span 行**访问 `row[-2]` 会越界崩溃 → `if len(row) < 2: return row, None`。
  宽松路径才会触发；崩溃时该书保持 0 书签而非写坏。
- 目录页可能含后续分册内容 → 连续 10 条定位不到即截断，避免把"下册目录"挂到本册。
- worklist 顺序会漂移：重跑时**不要**用旧日志的索引指认某本书，永远按路径核对。
- 若某本在旧日志显示很多书签、实测 0 → 多半是 worklist 顺序漂移指到别书，或该书 40+ 页是公式非目录（搜不到"目录"字样即图像目录，需另做"仅前台 OCR"）。

## Deliverable / report
收尾给用户：总 PDF 数、总书签数、本管线产出书数量、剩余 0 书签清单（标明哪些是可 OCR 救回的
正规书、哪些确实无目录）。绝不谎称 100% 覆盖。
