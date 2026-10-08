# AI & Math Translations Skill

`aimath-translations-skill` 用于将 AI、机器学习与数学书籍、论文、讲义及现有 LaTeX
项目翻译为中文 LaTeX，并对译稿进行原文对照、修复和编译校对。Skill 指令与参考规则
使用英文，本说明使用中文。

本项目 fork 自 [libinyam/mathtranslations-skill](https://github.com/libinyam/mathtranslations-skill)，
沿用其数学忠实度、引用、术语和 LaTeX 审校机制，增加 AI 书目与代码、伪代码保真约束。
这是独立维护的衍生项目；MathTranslations 的名称、模板文件名与审计配置名在涉及上游
资源时保留。来源及授权说明见 [NOTICE.md](NOTICE.md)，许可见 [LICENSE](LICENSE)。

## 核心规则

- 以出版原文 PDF 为内容依据；TeX 和 OCR 用于辅助恢复结构，疑似原文错误单独记录。
- 保留公式、假设、量词、证明、编号、交叉引用、引文、脚注和章节结构。
- **代码与伪代码关键字保持原文**：`for`、`do`、`end for`、`if`、`return`、
  `Input`、`Output` 等不译为中文；标识符、字面量、缩进、控制流、循环边界和行号同样保留。
  可翻译描述性标题、说明及不影响行为的自然语言注释；需检查 LaTeX 宏实际渲染的关键字。
- 模型、数据集、指标、库名和版本保持准确；字面提示词、输入输出示例作为原始数据保留。
- AI 公式核对张量维度、坐标轴、条件分布、归一化、梯度和优化更新；实验表格和曲线保留数据、
  单位、误差条、基线及结论强度，不补造实验结果。
- 数学交换图使用 `tikz-cd`；模型结构图、计算图、流程图和数据图根据内容使用 TikZ 或忠实原图。
- 分别进行语言术语、内容结构、编译与页面核对。静态审计结果不等于数学或算法正确性证明。

代码和 AI 书目细则见 [references/ai-code-fidelity.md](references/ai-code-fidelity.md)。

## 使用方式

```bash
git clone https://github.com/DBQDSS/aimath-translations-skill.git
```

将整个仓库目录按所用 Agent 的安装方式注册为 skill，或在任务中要求 Agent 读取根目录
`SKILL.md`。主 skill 的调用名与目录名相同：

```text
使用 $aimath-translations-skill 将这本机器学习书籍翻译为中文 LaTeX。
对照原始 PDF 保留数学内容和算法结构，代码与伪代码关键字保持原文，完成编译与校对。
```

审校已有项目：

```text
使用 $aimath-translations-skill 对照原始 PDF 审校这个 AI 书籍译稿，
重点检查算法关键字、代码保真、公式、实验图表、引用和排版。
```

不支持 skill 调用语法的 Agent 可以直接读取 `aimath-translations-skill/SKILL.md`。
`agents/openai.yaml` 是可选界面元数据，其他 Agent 可以直接使用 Markdown 指令。

提供原始 PDF，以及可用的 TeX、参考文献、OCR Markdown、图像和已有译稿即可。
现有项目沿用其模板与构建方式。仓库内置的是上游授权的 **legacy ctexart 单文件模板**
与 logo；`mathtranslation.cls`、`tools/build.sh`、`tools/figcrop.py` 等项目工具未随包提供，
使用这些变体时需有对应项目文件。Skill 不要求安装或运行书中的训练、下载与推理示例。

## 审计与依赖

基础审计仅依赖 Python 3 标准库：

```bash
python scripts/audit_latex.py path/to/project
python scripts/audit_latex.py path/to/project --strict
```

只有选用对应上游模板时，才启用模板审计：

```bash
python scripts/audit_latex.py path/to/project --profile mathtranslations --strict
```

`mathtranslations` 是上游模板配置名，保留以兼容原有工作流，不代表主 skill 的调用名称。
基础脚本检查重复标签、未定义引用与引文、缺失资源、待处理标记和编译日志；模板配置增加
术语、长证明、封面及排版检查。已支持的代码环境与行内代码从正文检查中排除；算法语法
不会因中文正文标点规则被要求改写。自定义环境、代码转义片段仍须人工核对。

LaTeX 编译需要项目相应的 TeX 引擎、字体及参考文献或索引工具；PDF 提取、渲染或某些
专项脚本需要 PyMuPDF，图像合成可能需要 Pillow，OCR 工作流还需可用的 OCR 引擎。
按所选任务安装依赖，不要求统一安装所有工具。

公式编号的旧版专项脚本通过 `AIMATH_ORIGINAL_PDF` 指定原书，
`AIMATH_PROJECT_ROOT` 指定项目（默认当前工作目录），并可配置页码偏移与编号带边界。
它们保留原来的特定标签和 OCR JSON 约定；使用前需读取该子 skill 的适用说明。
编译辅助脚本从 PATH 或 `TEXLIVE_BIN` 查找工具，构建步骤失败时立即返回失败。

已有审计回归测试可运行：

```bash
python -m unittest discover -s tests -v
```

## 专项审校 skills

以下子 skill 保留原名称，以对应已有脚本与实际模板。按需读取或单独注册；示例中的
书籍编号、OCR 数据格式、分页偏移和计数器方案需要对照当前项目确认，不可直接套用。
子 skill 中未随包提供的项目辅助脚本是可选例子，不能当作现成依赖。

| 目录 | 用途 |
|---|---|
| `latex-translation-fidelity-audit` | 结构、引用、术语、数学符号和残留正文审校；排除应保留的代码与算法英文 |
| `latex-eq-numbering-audit` | 对照原文核对公式编号 |
| `latex-array-diagram-audit` | 交换图布局、箭头方向及节点完整性 |
| `latex-display-layout-audit` | 公式版面修复，并保留公式编号 |
| `latex-footnote-fidelity-audit` | 脚注内容与落点完整性 |
| `latex-ocr-math-defect-audit` | OCR 引入的数学缺陷 |
| `latex-bookmark-anchor-audit` | PDF 书签和目录链接目标 |
| `mathtranslation-build-verify` | 项目编译、日志检查和页面核对 |
| `mathtranslation-cls-v31-upgrade` | 在明确需要时迁移到所提供的 v3.1 类文件 |
| `mathtranslation-hardref` | 将已确认目标的硬编码引用转换为交叉引用 |
| `math-pdf-bookmark` | 为 PDF 添加与标题位置对应的书签 |
| `pdf-scanned-ocr-bookmark` | 扫描 PDF 的文字层与书签工作流 |

## 目录

```text
aimath-translations-skill/
├── SKILL.md
├── README.md
├── NOTICE.md
├── LICENSE
├── agents/openai.yaml
├── assets/                         # 上游授权的 legacy 模板与 logo
├── references/
│   ├── ai-code-fidelity.md
│   ├── workflow.md
│   ├── latex-quality.md
│   ├── review-checklist.md
│   └── mathtranslations-template.md
├── scripts/audit_latex.py
├── tests/
└── skills/                         # 12 个专项审校 skill 及其已有脚本
```

## 来源与许可

本仓库继承上游 MIT 许可及其版权声明。随附模板与 logo 的授权来源沿用上游
`NOTICE.md` 记载，本 fork 不将上游资源改称为自己的原创资源。在线术语数据、原始书籍、
论文、代码示例与数据集仍受各自许可约束；仓库的 MIT 许可不替代这些作品的授权。
