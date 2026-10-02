# MathTranslations Agent Skill

一个平台无关的严谨数学翻译 Agent Skill。它把数学书籍、论文、讲义或已有
LaTeX 项目翻译成可编译、可校对、可维护的中文 LaTeX，并支持复核与修复
现有译稿。

本 Skill 不绑定 Codex 或任何特定模型、厂商和 Agent 框架。任何能够读取
Markdown 指令、访问项目文件并调用必要工具的 Agent 都可以使用。

本项目根据 [MathTranslations 数学翻译指南](https://mathtranslations.org/guide/)
整理为可执行工作流，并经 MathTranslations 创始人和版权所有者授权，内置
MIT 许可的 LaTeX 模板与 logo。在线术语表仍保持外部引用，以免固定过期数据。

## 能做什么

- 以出版 PDF 为内容核对依据，以源 TeX 辅助恢复结构和标记
- 保留定理、证明、公式、标签、引用、脚注、图表和层级结构
- 建立项目术语表，检查术语与符号一致性
- 支持 MathTranslations 官方模板的 `\newterm`、术语索引、长证明及习题答案互跳
- 插图按优先级处理：清晰原图优先截图、简单插图用 TikZ、交换图统一用 `tikz-cd` 重绘
- 行间公式统一 `align` 类环境、有序列表用 `enumerate`、中文引号用 TeX 引号写法
- 新项目可以直接从 skill 的 `assets/` 复制模板与 logo，无需额外下载
- 分离中文、数学、编译与版面三类校对
- 用内置脚本检查重复标签、未定义引用、缺失资源、模板漂移、连续展示公式、
  全角弯引号、手动编号列表和编译日志

## Agent 兼容性

Agent 最好具备以下能力：

- 读取 `SKILL.md` 和按需读取 `references/`
- 读取原始 PDF、MinerU Markdown、图片和 LaTeX 文件
- 在工作目录中创建和修改文件
- 执行 Python、XeLaTeX 或项目已有的构建命令
- 检查编译日志和生成的 PDF

`agents/openai.yaml` 只是 OpenAI/Codex 客户端可选的界面元数据。其他 Agent
可以忽略它，直接使用 `SKILL.md`。

## 安装与调用

将本仓库克隆到本地：

```bash
git clone https://github.com/libinyam/mathtranslations-skill.git
```

然后选择适合当前 Agent 的方式：

1. 将仓库复制到该 Agent 的 skills、rules 或 instructions 目录。
2. 在 Agent 配置中将本仓库或 `SKILL.md` 注册为一个 skill。
3. 在任务中直接要求 Agent 先读取本仓库的 `SKILL.md`。

支持 skill 调用语法的 Agent 可以使用：

```text
使用 $mathtranslations 把这篇数学论文翻译成中文 LaTeX，并编译校对。
所有交换图、态射图和适合节点箭头表达的数学图必须使用 tikzcd 重绘，
不得使用截图代替。
```

不支持 `$skill-name` 语法的 Agent 可以使用：

```text
请先读取 mathtranslations/SKILL.md，并严格按照其中的工作流，
把这篇数学论文翻译成中文 LaTeX，完成编译与校对。
所有交换图、态射图和适合节点箭头表达的数学图必须使用 tikzcd 重绘。
```

审校已有译本：

```text
使用 $mathtranslations 对照原始 PDF 复核这个中文 LaTeX 项目，修复引用和排版问题。
```

创建新译本时，只需向 Agent 提供原书 PDF、MinerU Markdown 以及提取的图片；
skill 会从自身 assets 复制模板和 logo 到项目目录。

## LaTeX 审计

```bash
python scripts/audit_latex.py path/to/project
python scripts/audit_latex.py path/to/project --strict
python scripts/audit_latex.py path/to/project --profile mathtranslations --strict
```

默认情况下，确定性错误返回非零状态；`--strict` 也会让警告返回非零状态，
适合 CI。`--profile mathtranslations` 还会检查 XeLaTeX、模板元信息、字体与
链接配置、术语键、长证明配对、句末标点、行间公式环境、引号写法、列表
环境、最终术语索引，以及 `mathtranslation.cls` 项目的 `\makecover`/
`\makecontents`/`\makebibliography` 调用、biblatex 是否重复加载等。

## 专项审校 Skills（`skills/`）

`skills/` 目录收录了一组围绕数学译本工作流的专项 skill，各自独立、带有自己的
`SKILL.md` 与脚本，可按需单独注册到 Agent，也可配合根目录的主 skill 使用：

| 目录 | 用途 |
| --- | --- |
| `latex-translation-fidelity-audit` | 全面审校中文译稿对原书的忠实度：结构（缺节、裸引用、习题标题、未译标题）与词汇/数学（算子宏、花体字母、残留英文）两个层面 |
| `latex-eq-numbering-audit` | 对照原书逐条核对公式编号，报告并修复缺号、错号、计数器未重置等问题 |
| `latex-array-diagram-audit` | 审校译稿中的图：array 环境图改绘为 tikzcd，已有 tikzcd 核对箭头方向与网格完整性 |
| `latex-display-layout-audit` | 对照原书审校行间公式版面（过度折行、假对齐、环境嵌套等），修复时不动公式编号 |
| `latex-footnote-fidelity-audit` | 证明 OCR 记录的每条脚注都进入了排版后的 PDF，并修复丢失者 |
| `latex-ocr-math-defect-audit` | 找出并修复 OCR 层在到达 LaTeX 之前悄悄损毁的数学内容（尤其脚注内公式） |
| `latex-bookmark-anchor-audit` | 审计并修复 PDF 书签/目录超链接锚点，解决"点击跳转位置不对" |
| `mathtranslation-build-verify` | 编译并可视化验证 LaTeX 文档（xelatex + biber + texindy），证明结果正确而非仅无报错 |
| `mathtranslation-cls-v31-upgrade` | 把旧模板（v1.x，ctexart）译本迁移到 `mathtranslation.cls` v3.1，含回归审计 |
| `mathtranslation-hardref` | 把译稿中手写的硬编码引用（定理 3.4、方程 (22)、跨章裸编号）转成可点击交叉引用 |
| `math-pdf-bookmark` | 批量为数学 PDF 添加精确到标题纵坐标的可点击书签（文本层与纯扫描两类） |
| `pdf-scanned-ocr-bookmark` | 用命令行 OCR 为纯扫描 PDF 加不可见文本层，并重建目录书签树 |

## 目录

```text
mathtranslations/
├── SKILL.md
├── agents/openai.yaml
├── assets/
│   ├── mathtranslations-translation-template.tex
│   └── logo.pdf
├── references/
│   ├── latex-quality.md
│   ├── mathtranslations-template.md
│   ├── review-checklist.md
│   └── workflow.md
├── scripts/audit_latex.py
├── tests/test_audit_latex.py
└── skills/                    # 专项审校 skills，各自独立可用
    ├── latex-translation-fidelity-audit/
    ├── latex-eq-numbering-audit/
    ├── latex-array-diagram-audit/
    ├── latex-display-layout-audit/
    ├── latex-footnote-fidelity-audit/
    ├── latex-ocr-math-defect-audit/
    ├── latex-bookmark-anchor-audit/
    ├── mathtranslation-build-verify/
    ├── mathtranslation-cls-v31-upgrade/
    ├── mathtranslation-hardref/
    ├── math-pdf-bookmark/
    └── pdf-scanned-ocr-bookmark/
```

## 来源与边界

工作流主要依据 MathTranslations 公开指南整理，并使用自己的表述和实现。
在线指南、术语资源与模板可能更新，实际项目应以
[指南页面](https://mathtranslations.org/guide/) 当前版本为准。

模板配置参考核对了官方
`mathtranslations-translation-template.zip`（2026-08-23 版；旧名
`MathTranslations-Template.c9598d4a8d56.zip` 为同一模板的早期发布）的
实际 TeX 与示例 PDF。模板 TeX 与 logo 经版权所有者授权，作为本仓库 MIT
许可内容公开；编译示例 PDF 未打包，因为运行 skill 不需要它。

**当前书籍项目实际使用的模板是 `mathtranslation.cls`（基于 ctexbook 的类文件，
由用户维护，不在本仓库内捆绑）**，与上面那个单文件 ctexart 模板是同源但不同的
两条线。本 skill 的 `references/mathtranslations-template.md` 已把 `mathtranslation.cls`
v3.x 作为主路径说明，单文件 ctexart 模板仅作历史参考。`assets/` 中仍保留
`mathtranslations-translation-template.tex` 与 `logo.pdf`（封面 logo 仍为
`mathtranslation.cls` 所用）。

数学翻译仍需要领域知识和人工判断。编译成功或脚本检查通过，不代表数学内容
已经正确；编号也要从生成的 PDF 文本中抽验，而不能只看退出码。

## License

本仓库内容（包括 `assets/mathtranslations-translation-template.tex` 与
`assets/logo.pdf`）采用 MIT License。在线术语数据与原始数学作品仍受其
各自许可和版权约束。
