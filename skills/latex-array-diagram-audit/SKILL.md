---
name: latex-array-diagram-audit
description: Audit diagrams in a LaTeX math translation against the original book PDF — both array-environment diagrams (convert to tikzcd so the rendered figure matches the source) and existing tikzcd blocks (verify arrow DIRECTIONS and grid completeness, i.e. catch reversed arrows, swapped rows and missing zero rows). Use when the user asks to check/redraw commutative diagrams, asks whether arrows are drawn backwards, or says diagrams are "not drawn with tikzcd".
agent_created: true
---

# LaTeX Array 环境交换图审计

## 概述

在数学书籍翻译/重排项目中，译者有时会用 `array` 环境临时画交换图。这些图虽然数学内容正确，但排版结构可能与原书（tikzcd 风格）不一致。本 Skill 提供一套可复用的工作流：定位所有 `array` 图示，与原书 PDF 逐页比对，将不符或过度简化的图改回 `tikzcd`，最后通过完整编译管线验收。

## 触发条件

- 用户说“检查交换图”“重画图”“array 环境画的图”“按原图重排”等。
- 用户说“很多图不是用 tikzcd 画的”或“检查箭头是否画反” → 走下面的 **tikzcd 反向审计**。
- 工作对象是 `ch*.tex` 等章节源文件，原书 PDF 在本地可用。

## tikzcd 反向审计（箭头方向 / 行列完整性）

当用户怀疑 `tikzcd` 箭头画反时，**不要只看源码猜**。必须：抽全量 tikzcd → 渲染重排稿对应页 →
与原书同页并排比对。实践中最常见的 4 类真错误不是“箭头画反”，而是：

1. **行序颠倒**：译文把 `G^n` 放在 `G^{n+1}` 之上（原书相反）。
2. **缺整行/整列**：零行、商行被漏掉（如 3 行图被压成 2 行）。
3. **缺前导/尾随零**：正合列网格少了 `0 \ar[r]` 与末列 `0`。
4. **竖直箭头该是单射/满射/等号时写成普通箭头** —— 要用 `hook` / `two heads` / `equal`。

**最大量的却是假警报**，别乱改：原书的 **域塔 / 素理想链 / diamond 图是用普通直线画的，没有箭头
笔画**（`m`、`p` 那些标签表示域的包含关系，不是映射）。译文里画成向上的 `\ar[u]` 是**正确的**。
判定方法见下面“用矢量笔画判定原图有没有箭头头”。

### A. 用 `main.aux` 定位原文页（比文本搜索可靠得多）

`\newlabel{<label>}{{<编号>}{<页>}{<section>}{<anchor>}{}}` 直接给出**印刷页**。
再按本项目固定的“印刷页 → PDF 页”偏移换算成 PDF 页（本项目 offset = 18），得到 PyMuPDF 的
0-based 索引 `index = 印刷页 + offset - 1`。

**务必用 aux，不要靠 `page.get_text()` 搜标签文字。** 中文正文里 `引理 4.9` 能被搜到，但**数学
内容是搜不到的** —— 例如 `Hom(G,\Q/\Z)`、`H^1(G,\Q)` 在抽取文本里根本匹配不上（数学字体断字），
纯文本搜索会给出“找不到”的假否定。经典踩坑：在 error 页附近反复翻，其实真页面在另一处。

同时注意：一个 `lemma` 的**陈述**和它的**证明里的图**通常不在同一页，图往往在下一页。

### B. 用矢量笔画判定原图有没有箭头头

原书 PDF 图是矢量线，`page.get_drawings()` 能列出每段笔画（`l`=直线、`re`=矩形、`q`=二次、`c`=曲线）。
两个用途：

- **自动找图页**：过滤 `≥5` 段直线且至少一段非水平的页面，即可在几百页里圈出所有含图的页，
  不必逐页看。
- **判定箭头有无**：若某张“diamond / 域塔”图的相关竖直方向**只有 `l` 直线段、没有任何短小的
  斜向笔画（箭头头）**，说明原书就是无箭头头的——译文的 `no head` / `\ar[u]` 不该改。

### C. 重建零填充正合列网格的配方

`n` 行内容 + 上下各一行零的 (n+2) 行网格：

```latex
\begin{tikzcd}[column sep=1.1em, row sep=1.1em]
 & 0 \ar[d] & 0 \ar[d] & 0 \ar[d] & \\
0 \ar[r] & B\cap C \ar[r, hook] \ar[d, hook] & B \ar[r, two heads] \ar[d, hook] & BC/C \ar[d, hook] \ar[r] & 0 \\
0 \ar[r] & A\cap C \ar[r, hook] \ar[d, two heads] & A \ar[r, two heads] \ar[d, two heads] & AC/C \ar[d, two heads] \ar[r] & 0 \\
0 \ar[r] & A\cap C/B\cap C \ar[r, two heads] \ar[d, two heads] & A/B \ar[r, two heads] \ar[d, two heads] & AC/BC \ar[r, two heads] \ar[d, two heads] & 0 \\
 & 0 & 0 & 0 &
\end{tikzcd}
```

要点：**顶行和底行只放零、且不画竖直箭头**（顶行的 `0 \ar[d]` 要画，底行的 `0` 不画）；
每行首个 `0` 用 `0 \ar[r]` 引出；末列 `0` 前用 `\ar[r]` 进入。中间行竖箭头按实际映射类型选
`hook` / `two heads` / `equal`。

### D. `array` → `tikzcd` 的最小转换

原来用 `\Big\downarrow` + `\xrightarrow` 拼的两行图，直接写成矩形 tikzcd 即可，
标签用 `\ar[r,"\phi_v"]`；竖直映射带名字用 `\ar[d,"\tau \mapsto \tau|_{L}"]`。
转换时**逐项保留原标签**（含右侧竖线上那种“映射到某物”的说明），不要顺手简化。

## 兼容旧版（仅 array 图）

### 1. 全量列出 array 环境

- 用 `Grep` 搜索 `\\begin\{array\}`，按文件汇总行号。
- 逐一读取源码，区分：
  - **真正的交换图**：方阵、矩形、带竖直箭头的两行图、field tower 等。
  - **可保留的 display**：单行/多行公式、滤列、长正合列文本等。

### 2. 定位原书对应页

- 记录翻译稿的“印刷页 → PDF 页”偏移（例如 v4.03 原书 PDF 页 = 印刷页 + 9）。
- 用 PyMuPDF 渲染原书对应页：
  ```python
  import fitz
  doc = fitz.open("原书.pdf")
  doc[pdf_page_index].get_pixmap(dpi=200).save("_orig_...png")
  ```
- 若位置不确定，用 `page.get_text()` 搜索关键词（如 "dimension shifting"、"Frobenius element"）。

### 3. 视觉比对

- 读取原书渲染页与翻译稿渲染页，检查：
  - 箭头/连线的方向、数量、起止节点。
  - 行列布局是否被简化（如 3D field tower 被压成 2×3 array）。
  - 是否有缺失元素（如竖直等号、对角线、双重竖线）。

### 4. 改用 tikzcd 重排

- 对确认不符的图，按原图节点与连线重建 `tikzcd`。
- 常用技巧：
  - 域扩张/素理想链的竖直线用 `no head`。
  - 等同映射用 `no head, double`。
  - 对角箭头用 `\ar[dl]`、`\ar[ur]` 等；注意空行会导致节点不存在，必要时用 `\ar[ddl]`。
  - 标签位置：`"label"` 在箭头左侧，`"label"'` 在右侧。

### 5. 编译验收

- 运行完整管线（本项目示例）：
  ```
  xelatex → biber → xelatex → texindy → xelatex
  ```
- `texindy` 必须带 `LC_ALL=C LANG=C`（否则 perl locale 报错退出 2，且**静默沿用旧 `main.ind`**，
  索引页码全错）。详见 `mathtranslation-build-verify` skill。
- 验收标准：`0 error`、`0 undefined reference`、`0 multiply-defined`。
- 清理临时 PNG（`_arr*.png`、`_orig_*.png`、`_verify_*.png`、`d*.png`、`tile_*.png` 等）与临时脚本。

## 注意事项

- 同文件多处编辑必须串行执行，避免并行 `Edit` 互相覆盖。批量改多个文件时，写一个 Python 脚本
  逐块 `replace`（每块断言 `count == 1`），比手工多次 `Edit` 安全且可复现。
- **保持行尾 CRLF**：本项目 `ch*.tex` 是 CRLF，脚本改文件时要 `newline=''` 读写字节，别让
  Python 把 `\r\n` 变成 `\n`（会产生整文件 diff 噪声）。
- 不要改动已完成译文或 `mycommand.sty`；新宏只加在 `main.tex`。
- 编辑完**必须**重编译并**渲染修复页看效果** —— 源码改对不等于排版正确（行列对齐、箭头头、
  嵌套分数在窄列里溢出，都只有看图才知道）。
- **模型看图能力与 Read 工具分情况说明**：
  过去笔记中曾出现“Read 无法渲染 PNG”的陈旧论断，这是因为**此前撰写该记录的模型是纯文本模型（Text-only）**，无法接收图像输入，从而将自身缺陷误判为工具或环境限制。实际上 `Read` 工具对多模态模型能完整渲染并注入图像。因此**必须按当前运行的模型分情况处理，先探一次**：
  - **情况一：当前模型为多模态视觉模型（支持看图）** → `Read` 正常渲染 PNG，直接进行目视核对（比对箭头方向、零行/商行完整性、双箭头与包含线等）。可将多张原书裁剪页拼成 3×3 大图批量核对，效率最高；
  - **情况二：当前模型为纯文本模型（无视觉能力）** → 调用 `Read` 会返回 `当前模型不支持图片` 或 `Content filtered`。此时必须降级为源码结构分析、PyMuPDF 矢量笔画提取（`page.get_drawings()`）与文本/公式上下文比对，并在报告中**如实告知用户当前模型无视觉能力、未进行直接目视核验**，严禁伪造核对结论。
