# AI & Math Translations Skill

将 AI、ML 与数学书籍、论文、讲义及现有 LaTeX 项目翻译为中文 LaTeX，支持原文对照、修复与编译校对。

[快速开始](#快速开始) · [使用文档](#使用文档) · [开发与维护](docs/development.md)

## 主要功能

- **翻译与审校**：覆盖正文、附录、脚注及算法说明，保留数学含义、符号、编号、引用和代码结构。
- **术语一致性**：结合原文语境建立项目术语表，人名保留原书拼写，如 `Cauchy 列`、`Fréchet 导数`。
- **LaTeX 校对**：检查公式、交换图、交叉引用、书签和编译结果，提供 12 个专项工具。
- **适配现有项目**：沿用已有模板与构建方式，也可选择随附的 MathTranslations legacy 模板。

## 快速开始

获取本仓库，按所用 Agent 的方式注册整个目录；也可直接让 Agent 读取 [SKILL.md](SKILL.md)。本项目不绑定特定模型。

提供原始 PDF 或 TeX、需要处理的范围，以及已有译稿和相关资源，然后提出任务：

```text
使用 $aimath-translations-skill 把当前文件夹中的 PDF 教材翻译成中文 LaTeX，并进行编译校对，最终交付编译好的 PDF。中文译本的相关彩色配图，直接使用英文原书配图即可，不必重新绘制；但对于适合用节点箭头表达（例如，章节关系/代数中的交换图等）的关系图，则使用 tikzcd 重绘，不使用截图代替。

你可以使用多个 subagent 帮你分章节并行翻译。
```

审校已有译稿：

```text
使用 $aimath-translations-skill 对照原始 PDF 审校现有 LaTeX 译稿，
检查漏译、术语、公式编号和引用，修复确认的问题并重新编译。
```

编译 PDF 需准备项目所需的 TeX 引擎、字体及参考文献工具。扫描和编译检查不能替代原文对照。

## 使用文档

| 文档 | 内容 |
|---|---|
| [完整工作流](SKILL.md) | 翻译约束、处理步骤与交付要求 |
| [术语政策](references/terminology-policy.md) | 术语选择与人名规则；随附术语表仅供候选参考 |
| [模板说明](references/legacy-template.md) / [模板适配](references/mathtranslations-template.md) | 随附 ctexart 模板与用户提供的类文件 |
| [开发与维护](docs/development.md) | 仓库结构、验证命令、专项工具与发布说明 |

## 致谢与许可

改编自 [libinyam/mathtranslations-skill](https://github.com/libinyam/mathtranslations-skill)，采用 [MIT 许可](LICENSE)。资产来源见 [NOTICE.md](NOTICE.md)；原书、论文及外部素材的授权需另行遵守。
