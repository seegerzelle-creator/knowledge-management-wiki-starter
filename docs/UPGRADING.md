# 从 v1.0 升级

先备份自己的知识库，把本候选解压到另一个目录。不要把新包直接覆盖已有库。

1. 对比 AGENTS、Rules、Schema、Templates 和三个既有 Skill，保留个人定制；按 CHANGELOG 逐项合并规则。
2. 新包使用 .agents/skills。检查你的客户端后再迁移旧 .codex/skills，避免同名 Skill 同时存在导致重复发现。不迁移本机全局 Skill。
3. 个人 index、log、ThinkDesk 保留原位；.example.md 只是空白模板。没有对应文件时才创建。
4. 不复制示例到自己的正式 Raw/Wiki，不重置 reviewed、ingest_disposition 或审批状态。
5. 先对一条非敏感 Capture 做背景确认，再对一条 External 做只读 ingest 预览；确认行为符合预期后再扩大使用。
6. 本次不回填历史 metadata，不更改既有正式领域，不启用标签体系、自动化、同步或 RAG。

新包保留模板的 work 领域，不强制继承任何个人库的 startup 领域。
知识库使用后只能运行普通校验；--distribution 专门检查无真实内容的分发包。
Git ignore 不会自动停止跟踪旧笔记；公开前检查实际 tracked/staged 清单，避免把个人历史作为模板分发。

当前适配路径依据：[Codex 官方 Skill 文档](https://learn.chatgpt.com/docs/build-skills)（2026-10-24 查阅）。
