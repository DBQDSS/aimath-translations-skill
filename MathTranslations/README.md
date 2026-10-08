# MathTranslations 本地资料

本目录为 `aimath-translations-skill` 提供无需访问 MathTranslations 网站的基础资料。
资料按固定版本随仓库分发；用户提供的模板、原稿及明确的项目约定优先。

| 文件 | 用途 |
|---|---|
| [guide.md](guide.md) | 本地制作指南与资料入口，skill 使用英文 |
| [legacy-template.md](legacy-template.md) | 随附 ctexart 模板的真实接口、准备方法和编译要求 |
| [template-profile.md](template-profile.md) | 用户提供 ctexbook 类文件时的适配说明 |
| [terminology.md](terminology.md) / [terminology.tsv](terminology.tsv) | 本地数学及 AI/ML 基础术语与义项说明，不是官网数据库导出 |
| [templates/legacy/](templates/legacy/) | 已授权的模板、logo 与 MIT 许可副本 |
| [sources.json](sources.json) | 来源、核对日期、收录范围及文件 SHA-256 |

选择随附模板时，先读 `legacy-template.md`，再将模板、logo 和许可复制进译稿项目，
修改项目副本。`mathtranslation.cls`、TeX 引擎、字体及项目专用脚本未随包提供。
原 `assets/` 路径保留为兼容副本；新流程使用本目录中的资料，两份模板及 logo 内容一致。

官网地址仅用于追溯来源。日常翻译不访问官网、不自动更新资源；需要新版时再明确安排
维护任务，核对来源、许可和兼容性后更新。网站失效不影响已收录资料的读取和使用。
