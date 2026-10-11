# AI & Math Translations Skill

将 AI、机器学习与数学书籍、论文、讲义及现有 LaTeX 项目翻译为中文 LaTeX，并支持原文对照、修复与编译校对。主入口为 [SKILL.md](SKILL.md)，不绑定特定模型；可按所用 Agent 的方式注册整个目录，或直接要求 Agent 读取入口文件。

本项目改编自 [libinyam/mathtranslations-skill](https://github.com/libinyam/mathtranslations-skill)。来源及资产说明见 [NOTICE.md](NOTICE.md)，许可见 [LICENSE](LICENSE)。

## 翻译约束

- 先确认用户指定的版本和范围，以该版本原文为内容依据；OCR 和抽取文本仅作辅助。全文任务包括附录、脚注、补充证明与前后置内容，并记录逐项覆盖情况。
- 保留定义、假设、量词、证明、符号、编号、引用与结论强度。疑似原文错误单独记录，不静默改正。
- **人名及人名衍生术语保留原书拼写**：`Cauchy sequence` → `Cauchy 列`，`Fréchet derivative` → `Fréchet 导数`，`Markov chain` → `Markov 链`。保留重音、连字符和原文衍生形式；`Gaussian` 不自行反推为 `Gauss`。规则覆盖标题、正文、脚注、图表和索引，不限于首次出现。
- 保留代码、伪代码关键字、标识符、字面量和结构；翻译算法内的自然语言描述与安全的解释性注释。不能将整个算法块豁免为“不译”。
- 模型、数据集、API、字面提示词、实验数据及单位保持源文忠实。翻译任务本身不要求运行训练或推理代码。
- 沿用现有项目的模板和构建方式，仅在选择 MathTranslations 模板时应用其专属排版约定。
- 静态扫描只是候选检查；编译成功不能证明数学、术语、编号或全文覆盖正确。

## 术语表如何使用

[术语政策](references/terminology-policy.md) 是统一规则入口。[候选 TSV](references/terminology/terms.tsv) 的 74 条记录均为 `candidate`，**没有逐条外部权威核验，不是强制译名表，也不是官网数据库导出**。

先核对原文定义、领域和义项，再建立项目术语表，记录源文位置、采用形式、证据和状态。`compact` 的“紧 / 紧致”、不同微分变量下的 `score` 等不能只按单词匹配；不得把多候选单元格整体复制成正式译文。与原文语义、人名保留规则冲突的既有译名应记录并纠正，不做全局机械替换。无证据时保留原文、标记待核验，不能宣称“已获共识”。

## 使用示例

```text
使用 $aimath-translations-skill 把当前文件夹中的 PDF 教材翻译成中文 LaTeX，并进行编译校对，最终交付编译好的 PDF。中文译本的相关彩色配图，直接使用英文原书配图即可，不必重新绘制；但对于适合用节点箭头表达（例如，章节关系/代数中的交换图等）的关系图，则使用 tikzcd 重绘，不使用截图代替。

你可以使用多个 GPT-6-sol-high 作为 subagent 帮你并行翻译。
```

审校已有项目时，提供原始版本、译稿和可用的模板、TeX、图片、参考文献及构建说明，明确需要检查的范围。不支持 `$skill-name` 的 Agent 可直接读取本目录的 `SKILL.md`。`agents/openai.yaml` 是可选界面元数据。

## 目录和模板

```text
aimath-translations-skill/
├── SKILL.md
├── README.md / NOTICE.md / LICENSE
├── agents/openai.yaml
├── assets/                      # 唯一一份 legacy 模板和 logo
├── references/                  # 工作流、术语政策、模板及审校说明
│   ├── terminology/terms.tsv    # 候选术语及状态、来源限制
│   └── resource-provenance.json # 来源范围和资产哈希
├── scripts/audit_latex.py
├── skills/                      # 12 个专项审校入口及辅助脚本
└── tests/                       # 行为回归测试
```

普通使用不依赖官网可用，也不会自动刷新本地资料。需要查证有争议术语时按任务条件使用可靠来源，并记录实际查证范围。

选择随附模板时，按 [legacy 模板说明](references/legacy-template.md) 从 `assets/` 复制 TeX 和 logo，同时保留根目录 MIT 许可。它是固定的 ctexart 模板，不是最新版承诺。用户提供 `mathtranslation.cls` 时读 [模板适配说明](references/mathtranslations-template.md)，核实实际接口；类文件和项目专用构建工具未随包提供。

本次移除了重复的 `MathTranslations/` 资料树：模板回归 `assets/`，模板说明和来源记录归入 `references/`，术语表移至 `references/terminology/terms.tsv`。旧路径和旧 TSV 的 `chinese` 列已迁移为 `candidate_zh`；依赖旧路径的外部脚本需更新。12 个专项 skill 名称保持不变。

## 审计与验证

基础审计仅依赖 Python 3 标准库，从本仓库根目录运行：

```bash
python scripts/audit_latex.py path/to/project
python scripts/audit_latex.py path/to/project --strict
python scripts/audit_latex.py path/to/project --profile mathtranslations --strict
python -m unittest discover -s tests -v
```

模板配置仅适用于所选 MathTranslations 模板。它检查标签、引用、资源、日志及特定模板约定，不能判定每个术语是否合适。漏译扫描为：

```bash
python skills/latex-translation-fidelity-audit/scripts/residual_english_scan.py path/to/project
```

英文人名与代码不是自动翻译指令；扫描输出须回源判断。章节计数与旧式公式编号工具可能依赖特定文件名、OCR 结构、页码偏移和编号模型，使用前阅读对应说明。未覆盖文件须另行审查。修改引用前确认目标和渲染编号，先预览差异；歧义不得靠猜测批量修复。

LaTeX 编译需要实际项目的 TeX 引擎、字体、参考文献及索引工具。PDF 专项工具可能需要 PyMuPDF、Pillow 或 OCR 引擎，按需配置。`AIMATH_ORIGINAL_PDF`、`AIMATH_PROJECT_ROOT` 和 `TEXLIVE_BIN` 等配置示例不包含个人机器路径。

| 专项入口 | 用途 |
|---|---|
| `latex-translation-fidelity-audit` | 覆盖、引用、术语、符号、算法说明 |
| `latex-eq-numbering-audit` | 原文公式编号对照 |
| `latex-array-diagram-audit` | 交换图节点、箭头和布局 |
| `latex-display-layout-audit` | 展示公式版面 |
| `latex-footnote-fidelity-audit` | 脚注内容及落点 |
| `latex-ocr-math-defect-audit` | OCR 数学缺陷 |
| `latex-bookmark-anchor-audit` | 书签和目录链接目标 |
| `mathtranslation-build-verify` | 编译、日志及页面核对 |
| `mathtranslation-cls-v31-upgrade` | 用户指定的类文件迁移 |
| `mathtranslation-hardref` | 已确认目标的硬编码引用转换 |
| `math-pdf-bookmark` | PDF 标题书签 |
| `pdf-scanned-ocr-bookmark` | 扫描 PDF 文字层与书签 |

## 发布与隐私

发布 skill 时排除 `.git/`、缓存、日志、私人原稿和项目配置；需要干净发布包时从审核过的文件创建新仓库或压缩包。忽略规则不会清除旧 Git 历史中的数据。译稿封面、PDF 元数据、批注及源文件中的译者或模型信息应按用户选定的公开署名填写，不复制本机账号、私人路径或内部信息。

保留上游版权和公开来源不属于隐私泄露。仓库 MIT 许可不替代原书、论文、数据库和外部素材的授权。本次审查范围与测试结果见交付的任务报告。
