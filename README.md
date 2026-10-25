# 个人 LLM 知识库 · Codex 启动包

把收藏、灵感和经验，变成以后能查证、能继续思考的知识。

用本地 Markdown 保存原始材料（Raw），再把确认后的整理放进知识页（Wiki）。其中 **Seed 就是一张可继续追踪的问题卡**，不要求你先有答案。

**v1.1.0-rc.3 · 公开预览版（Pre-release）。** 许可：[MIT](LICENSE)。

## 先试一条，暂不配置

1. [下载 v1.1.0-rc.3 启动包 ZIP](https://github.com/seegerzelle-creator/knowledge-management-wiki-starter/releases/download/v1.1.0-rc.3/llm-wiki-starter-v1.1.0-rc.3.zip)，解压完整目录，保留隐藏目录 `.agents/`。
2. 用 Codex 打开这个文件夹，发送：

```text
请读取 AGENTS.md 和 FIRST-RUN.md。
跳过个人配置，保留通用默认值，先说明怎样保存第一条 Capture。
```

3. 把下面尖括号里的部分换成你自己的非敏感问题或想法，再发送：

```text
Capture：<你的原文>
```

Agent 会先原样保存，再问这条记录的背景。背景确认后，给你看理解是否准确；只有看过具体草案并批准，才创建问题卡。每一步都会说明当前状态、会改哪些文件、下一句可以怎样回复。详见 [第一次使用](FIRST-RUN.md)。

只想存下来，使用 `仅保存 Capture：<你的原文>`，保存并验证后就停止。

希望先设置称呼、用途和隐私范围，可以选择 [个性化配置](FIRST-RUN.md#个性化配置可选)，也可以用过几条资料后再配置。

## 日常入口

| 你可以说 | 会发生什么 |
|---|---|
| 检查新资料 | 只读列出材料和待确认问题 |
| 摄取这条资料 | 展示具体整理草案；按有效授权写入并验证 |
| 整理这篇经历 | 分清当时信息、判断、行动与结果 |
| Output：<草稿> | 原样保存，再预览作品状态 |
| 查看审批台 | 查看待决定事项；未初始化时只展示模板 |
| 体系检查 | 检查链接、状态、证据和维护问题 |

先看 [虚构示例](Examples/README.md)，完整规则入口见 [AGENTS.md](AGENTS.md)。

## 使用条件与个人资料

需要支持项目规则和本地文件访问的 Codex；Obsidian 可选。本包不额外要求数据库或 API 服务。文件保存在本地，AI 推理仍取决于 Codex 的账号、网络与模型。

真实 Raw/Wiki、个人配置、导航日志与审批记录默认由 `.gitignore` 忽略。它们在你获准写入后按需创建；公开包只提供空白目录和 `.example.md` 模板。忽略规则不能移除已被 Git 跟踪的内容。

示例全部虚构，不是你的知识或授权。原文保全与确认关口是 Agent 行为约定，重要结果仍需人工检查和可恢复备份。

<details>
<summary>目录、检查与升级</summary>

```text
Raw/            原始资料：外部材料、捕捉、经历、作品
Wiki/           知识页：来源摘要、问题卡、实体、概念、综合判断
Rules/          工作规则
Templates/      页面模板
Examples/       虚构示例
.agents/skills/ 四个项目级 Skill
Schema.md       字段与页面结构
Blueprint.md    未来扩建条件
*.example.md    个人导航、日志与审批台模板
```

Skill 目录依据 [Codex 官方说明](https://learn.chatgpt.com/docs/build-skills)。未显示时可重新打开项目，或明确要求读取对应 SKILL.md；其他 Agent 和旧客户端尚未完成兼容验证。

只有辅助脚本和检查需要 Python 3.10+，使用标准库。在根目录运行：

```bash
python3 scripts/validate_package.py --distribution
python3 -B -m unittest discover -s tests -v
```

第一条检查空白分发包；日常使用后去掉 `--distribution`。静态检查不证明事实、翻译或 Agent 执行正确。

已有知识库先看 [升级说明](docs/UPGRADING.md)，不要覆盖自己的文件。变更见 [CHANGELOG.md](CHANGELOG.md)。

</details>

贡献见 [CONTRIBUTING.md](CONTRIBUTING.md)，许可与素材范围见 [LICENSE](LICENSE)、[NOTICE.md](NOTICE.md)。
