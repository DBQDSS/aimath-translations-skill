---
name: latex-display-layout-audit
description: Audit display-math layout in a re-typeset LaTeX math book against the ORIGINAL book PDF, then repair anomalies — over-wrapped formulas, "fake alignment" blocks (align misused for hanging indent), display envs nested in display envs, and spaced hyphens inside \text{} — WITHOUT changing any equation number. Use when a user shows a badly laid-out formula page and says "compare with the original" / "原书对比" / "奇奇怪怪的排版".
agent_created: true
---

# 重排书显示公式版面审计（对照原书 PDF）

## 何时用

- 用户贴出一页排版怪异的公式，说「和原书对比」「根据原书改」「彻底排查这种情况」。
- 对象是重排/翻译的数学书（`chapters/*.tex` + 一个 `.cls`），**原书 PDF 在本机可用**。
- 典型症状：
  1. **过拆**：本可 1–2 行的公式被拆成 5–7 行（原书栏窄，重排版心宽）。
  2. **假对齐**：`align` 里用 `&\quad` 做悬挂缩进，整块被推到右侧 / 末行反而左对齐。
  3. **嵌套显示环境**：`gather(ed)` / `aligned` / `split` 套在 `align` 里。
  4. **`\text{}` 内空格连字符**：`Hilbert - Schmidt`（OCR 残留）。

## 第一原则：先拿到原书页

**先找原书 PDF，再动手。** 不要凭 LaTeX 直觉重构。

若原书 PDF **自带文本层**（多数 Springer 数字版 / OCR 版都有），直接：

```python
import pymupdf
orig = r"<原书.pdf>"
d = pymupdf.open(orig)
pgs = [i+1 for i in range(d.page_count) if "<待查短语>" in d[i].get_text()]
print(pgs)                      # 定位页
pg = d[pgs[0]-1]
pg.get_pixmap(matrix=pymupdf.Matrix(4,4), dpi=300).save("orig.png")
# 精确裁剪某几行：先取 bbox，再 clip
for b in pg.get_text('dict')['blocks']:
    for l in b.get('lines', []):
        t = ''.join(s['text'] for s in l['spans'])
        if 'Re T' in t: print(t, l['bbox'])
```

- **页码换算**：原书 PDF 页 ≈ folio + 偏移（本项目 Yosida 为 +16，folio 306 → PDF p322）。
  偏移 = 第一次搜索命中页 − 该页页眉印的 folio。
- OCR 文本层的行 bbox **可能按小片段乱拆**，只用来定位，不要当排版真值。
  **字形真值看渲染图**：`matrix=Matrix(10~18,10~18)` 高倍裁剪。
  （前提：当前模型能看图。能否 Read PNG 取决于运行中的模型是否多模态，**先探一次**；若 Read 拒绝
  图片（`Content filtered` / `当前模型不支持图片`），则退回到量测数据（行数、bbox 中心、字体名）
  作判据，并**如实告知用户**未能做视觉核对。）

## 第二原则：排版真值来自几何量测

判断「原书怎么排」看三件事，而不是看源码：

1. **几行**：行数（大公式 2 行 vs 我们 5 行）。
2. **居中还是对齐**：取每行 bbox 的 `(x0+x1)/2`，与正文块中心比较。
   本项目中：正文块中心 ≈ 219.7pt，原书 λ₁ 行中心 219.5 → **居中**。
3. **是什么字体**：`\Re`（ℜ 花体）vs 斜体 `Re` 是两个不同字形，渲染图上一目了然。

## 工作流

### 步骤 1：定位源码块 + 原书页

```bash
# 用公式里的独特片段搜源码（注意 `&` 和 `\\`）
grep -rn 'lambda_{j-1} + i \\\\mu_{j-1}\|E _ {\\\\lambda_{j}' chapters/*.tex
```

再在原书 PDF 里搜同一短语找页。

### 步骤 2：判定异常类型（跑扫描器）

用 `scripts/scan_layout_oddities.py`（见下，把 `ROOT` 指向 `chapters/` 的父目录）：

```bash
python scripts/scan_layout_oddities.py
```

输出三类：
- **(A) 显示环境嵌套显示环境** —— 最可靠的"假对齐"探测器，命中少而准。
- **(B) 编号环境全 `\notag`** —— 多为合法的多行无编号推导，**抽查即可，别批量改**。
- 行首 `&` 启发式 —— **命中太多、无区分度，别用**（本项目 168 命中，199 个是正常的）。

> 嵌套 (A) 里只有部分是真错：本项目 3 处中 2 处渲染正常（其中 1 处还带真实编号 `\label`，
> **绝不能动**）。**必须逐处渲染确认真错再改。**

### 步骤 3：改写（**保住编号是红线**）

**最关键的判断**：该块是编号环境吗？逐行看 `\notag` / `\label`。

| 原块情况 | 能否改结构 | 做法 |
|---|---|---|
| 每行都有 `\notag`（不产生编号） | ✅ 可自由改 | 换成 `\[ \begin{gathered}…\end{gathered} \]` |
| 有 `\label` / 无 `\notag`（产生编号） | ❌ **禁改** | 只在必要时调行内断点 |
| 混合 | ⚠️ 逐个核 | 保住编号行数 = 原编号个数 |

**范式**：原书"假对齐块"通常是**居中**的，不是真对齐。所以：

```latex
% 原（错）：align 里塞 gathered + &\quad 假缩进
\begin{align}
&\quad \begin{gathered} <5 行大公式> \end{gathered} \notag \\
\lambda_{1}& = -\alpha - \frac{\varepsilon}{\sqrt{2}} \notag \\
&\quad \leqq \lambda_{2} \leqq \dots \notag \\
&\quad = \sup \dots \notag
\end{align}

% 改（对）：两个 \[…gathered…\]，大公式 2 行 + 每个条件各 1 行，全部居中
\[
\begin{gathered}
<大公式行 1> \\
<大公式行 2>
\end{gathered}
\]
\[
\begin{gathered}
\lambda_{1} = \dots \leqq \lambda_{n} = \alpha = \sup\dots, \\
\mu_{1} = \dots, \\
\left(\sup\dots\right)^{1/2} \leqq \varepsilon .
\end{gathered}
\]
```

**行数按原书**：原书大公式几行就几行（在 160mm 版心下通常能放下原书的断点）。

### 步骤 4：批量小修（`\text{}` 空格连字符）

先**用原书验证**该词的原书写法（`self-adjoint` 114× vs `self - adjoint` 0× → 闭合是对的）。
只改 `\text{... - ...}` 内部的 ` - ` → `-`，用 `scripts/fix_hyphen_spacing.py`。

### 步骤 5：编译 + 验证（缺一不可）

```bash
pdflatex -interaction=nonstopmode main.tex   # × 2~3 遍；避免 latexmk 的 Perl 编码坑
grep -c "^!" main.log                        # 必须 0
grep "Output written" main.log               # 页数
grep -c "newlabel" main.aux                  # 与原值对比，必须不变
grep -i "may have changed" main.log          # 必须空
```

**铁证**：改动前后 `.aux` 的 `\newlabel` 条数与编号**完全不变**（本项目 1928 条不变）。
若页数变了 → 索引硬编码页码要重标定（见项目 `rebase_index.py`）。

### 步骤 6：出对比图

把**原书裁剪**与**修复后裁剪**上下叠放，缩放到同宽，标注 folio：

```python
from PIL import Image, ImageDraw
a=Image.open('orig.png'); b=Image.open('ours.png'); W=1200
a=a.resize((W,int(a.height*W/a.width))); b=b.resize((W,int(b.height*W/b.width)))
cv=Image.new('RGB',(W+40,a.height+b.height+150),'white'); d=ImageDraw.Draw(cv)
d.text((22,18),'ORIGINAL — folio NN',fill=(180,0,0)); cv.paste(a,(20,45))
d.text((22,a.height+110),'RE-TYPESET — after fix',fill=(0,0,180)); cv.paste(b,(20,a.height+140))
cv.save('judge/fix_before_after_vs_orig.png')
```

## 脚本

- `scripts/scan_layout_oddities.py` —— 扫 (A) 嵌套显示环境 / (B) 全 notag 编号环境。
  改 `ROOT` 指向包含 `chapters/` 的目录即可。
- `scripts/fix_hyphen_spacing.py` —— 关掉 `\text{}` 内空格连字符；自动备份、保留 CRLF。

## 踩坑清单

1. **CRLF**：`.tex` 常是纯 CRLF。编辑前先验 `raw.count(b'\n') == raw.count(b'\r\n')`，
   用「读 bytes → 分 `\r\n` → 改切片 → 拼回」的方式改，别用会规范化行尾的工具。
2. **别相信截断的输出**：`line[:170]` 会把 `\notag` 截成 `\nota`，误判成笔误。
   要判定内容就用完整行。
3. **latexmk 在本机中文 Windows 会崩**（Perl 代码页），报 "Couldn't open .bcf" +
   几千条未定义引用。**这不是文档问题**，直接用 `pdflatex`+`biber` 序列。
4. **`wc -l` 不是压缩效果的度量**：重排公式环境会改变物理行数（可能反增），
   但逻辑显示行是真的减少。看 **PDF 页数**。
5. **嵌套环境护栏**：合并内层会撑宽外层 `align` 列，把整行推出页面。
   批量操作显示环境时，遇到嵌套必须跳过。
6. **不确定的字形/记号不要擅自全改**：如 `\Re`(ℜ) vs 斜体 `Re` 涉及全书 196 处，
   属记号体系决策 → **出证据、问用户**，别自己拍板。
