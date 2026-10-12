# 开发与维护

[返回 README](../README.md)

本文面向维护者和直接运行审校脚本的使用者。翻译规则以 [SKILL.md](../SKILL.md) 为入口，术语决策遵循[术语政策](../references/terminology-policy.md)。

## 仓库结构

```text
aimath-translations-skill/
├── SKILL.md                     # Agent 主入口
├── README.md / NOTICE.md / LICENSE
├── agents/openai.yaml           # 可选界面元数据
├── assets/                      # 当前入口使用的 legacy 模板与 logo
├── references/                  # 工作流、术语政策、模板及审校说明
│   ├── terminology/terms.tsv    # 候选术语及状态、来源限制
│   └── resource-provenance.json # 来源范围和资产哈希
├── docs/development.md          # 本文
├── scripts/audit_latex.py       # 基础静态审计
├── skills/                      # 12 个专项入口及辅助脚本
├── tests/                       # 行为回归测试
└── MathTranslations/            # 仓库仍保留的旧资料树
```

当前主入口引用 `assets/` 和 `references/`。仓库仍保留 `MathTranslations/` 旧资料树，其中部分说明与当前入口不一致；维护时应核对实际引用，不能假定旧目录已经删除。外部脚本若依赖旧路径或旧 TSV 的 `chinese` 列，应核对与当前 `references/terminology/terms.tsv` 的 `candidate_zh` 字段是否兼容。

## 资料与模板维护

- [候选术语表](../references/terminology/terms.tsv) 不经过逐条外部权威核验，不是强制译名表或官网数据库导出。采用前核对原文定义、领域和义项，在项目术语表记录源文位置、采用形式、证据与状态；不要机械替换或把多候选单元格整体写入译文。
- 人名及其衍生形式保留原书拼写、重音与连字符，例如 `Gaussian` 不自行反推为 `Gauss`。规则覆盖标题、正文、脚注、图表和索引，完整要求见[术语政策](../references/terminology-policy.md)。
- 普通使用不依赖官网可用，不自动刷新本地资料。查证有争议术语时记录实际来源和查证范围；没有证据时标记待核验。
- 随附模板是固定的 ctexart 快照。按 [legacy 模板说明](../references/legacy-template.md) 复制 `assets/` 中的 TeX、logo 和根目录 MIT 许可，修改项目副本。
- 用户提供 `mathtranslation.cls` 时，按[模板适配说明](../references/mathtranslations-template.md) 核实实际接口；类文件及项目专用构建工具未随包提供。
- 更新资产时核对 [NOTICE.md](../NOTICE.md) 和[来源记录](../references/resource-provenance.json) 中的来源范围、许可及哈希。

## 审计与验证

基础审计仅依赖 Python 3 标准库，从本仓库根目录运行：

```bash
python scripts/audit_latex.py path/to/project
python scripts/audit_latex.py path/to/project --strict
python scripts/audit_latex.py path/to/project --profile mathtranslations --strict
```

它检查标签、引用、资源、日志及特定模板约定。`mathtranslations` 配置仅适用于所选 MathTranslations 模板，不能判定每个术语是否合适。

漏译候选扫描：

```bash
python skills/latex-translation-fidelity-audit/scripts/residual_english_scan.py path/to/project
```

英文人名与代码不是自动翻译指令，扫描结果须回源判断。代码和伪代码保留语法、标识符、字面量与结构，但算法内的自然语言描述仍需翻译。翻译本身不要求运行训练或推理代码。

修改脚本或工作流后，运行行为回归测试：

```bash
python -m unittest discover -s tests -v
```

章节计数与旧式公式编号工具可能依赖特定文件名、OCR 结构、页码偏移和编号模型，使用前阅读对应说明。未覆盖文件须另行审查；修改引用前确认目标和渲染编号，先预览差异，不凭猜测批量修复。

LaTeX 编译需要实际项目的 TeX 引擎、字体、参考文献及索引工具。PDF 专项工具可能需要 PyMuPDF、Pillow 或 OCR 引擎，按需配置。`AIMATH_ORIGINAL_PDF`、`AIMATH_PROJECT_ROOT` 和 `TEXLIVE_BIN` 等配置应按实际环境填写，公开示例不包含个人机器路径。

静态扫描只生成待核查线索；编译成功不能证明数学、术语、编号或全文覆盖正确。交付前仍需按[审校清单](../references/review-checklist.md) 对照原文和渲染页面。

## 专项工具索引

| 入口 | 用途 |
|---|---|
| [latex-translation-fidelity-audit](../skills/latex-translation-fidelity-audit/SKILL.md) | 覆盖、引用、术语、符号、算法说明 |
| [latex-eq-numbering-audit](../skills/latex-eq-numbering-audit/SKILL.md) | 原文公式编号对照 |
| [latex-array-diagram-audit](../skills/latex-array-diagram-audit/SKILL.md) | 交换图节点、箭头和布局 |
| [latex-display-layout-audit](../skills/latex-display-layout-audit/SKILL.md) | 展示公式版面 |
| [latex-footnote-fidelity-audit](../skills/latex-footnote-fidelity-audit/SKILL.md) | 脚注内容及落点 |
| [latex-ocr-math-defect-audit](../skills/latex-ocr-math-defect-audit/SKILL.md) | OCR 数学缺陷 |
| [latex-bookmark-anchor-audit](../skills/latex-bookmark-anchor-audit/SKILL.md) | 书签和目录链接目标 |
| [mathtranslation-build-verify](../skills/mathtranslation-build-verify/SKILL.md) | 编译、日志及页面核对 |
| [mathtranslation-cls-v31-upgrade](../skills/mathtranslation-cls-v31-upgrade/SKILL.md) | 用户指定的类文件迁移 |
| [mathtranslation-hardref](../skills/mathtranslation-hardref/SKILL.md) | 已确认目标的硬编码引用转换 |
| [math-pdf-bookmark](../skills/math-pdf-bookmark/SKILL.md) | PDF 标题书签 |
| [pdf-scanned-ocr-bookmark](../skills/pdf-scanned-ocr-bookmark/SKILL.md) | 扫描 PDF 文字层与书签 |

## 发布与隐私

发布 skill 时排除 `.git/`、缓存、日志、私人原稿和项目配置；需要干净发布包时从审核过的文件创建新仓库或压缩包。忽略规则不会清除旧 Git 历史中的数据。

译稿封面、PDF 元数据、批注及源文件中的译者或模型信息应按用户选定的公开署名填写，不复制本机账号、私人路径或内部信息。

保留上游版权和公开来源不属于隐私泄露。仓库 MIT 许可不替代原书、论文、数据库和外部素材的授权。
