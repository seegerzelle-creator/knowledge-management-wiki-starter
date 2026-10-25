---
name: web-clipper-library-note
description: Convert Obsidian Web Clipper notes and Raw/External materials into readable, traceable, library-grade Raw notes. Use for articles, webpages, book excerpts, papers, courses, prompts, videos, podcasts, interviews, talks, English transcripts needing a Chinese reading layer, user-provided Chinese transcripts needing evidence alignment, and existing bilingual transcript maintenance. Preserve original evidence and playable media embeds; do not create Wiki conclusions.
---

# 原始资料馆藏化

把外部剪藏整理成可阅读、可查证、可供未来 ingest 回溯的 Raw 馆藏笔记。Raw 是图书馆里的书，不是摘要卡或正式知识结论。

## 核心边界

- 只处理 `Raw/External/` 和明确指定的外部资料。
- 保留 URL、作者、原始标题、日期线索、正文、逐字稿、提示词和可播放媒体嵌入。
- 只使用轻量 Raw metadata；不添加正式 `domains`、`use_cases`、证据结论或 Wiki 候选字段。
- 不创建或更新 Wiki 页面。
- 不用摘要、润色稿或中文译文覆盖原始证据。
- 不批量移动、删除、合并或归档 Raw。

## 必须读取

修改前读取：

1. `AGENTS.md`
2. `Rules/raw-rules.md`
3. `references/raw-library-note-format.md`

自主翻译继续读取 `references/transcript-workflow-modes.md` 和 `references/transcript-translation-quality.md`；用户提供中文稿继续读取 `references/transcript-workflow-modes.md` 和 `references/user-chinese-transcript-alignment.md`。

## 模式

1. 普通外部资料：保留正文，增加简洁阅读脚手架。
2. 自主翻译：从英文证据生成明确标注的中文阅读层。
3. 用户中文稿对齐：保留用户措辞，只做对齐、轻度规范和排版。
4. 已有双语维护：修复缺漏、错位、格式和 provenance，不无故重译。

## 主流程

1. 定位目标，确认路径和范围。
2. 固定来源、标题、作者、简介、章节、时间戳和原文。
3. 规范轻量 Raw metadata，保持 `status: raw`。
4. 按类型执行；长逐字稿优先使用 `scripts/bilingual_transcript_tool.py`。
5. 生成馆藏信息、读前说明、导航和质量说明。
6. 检查中英文证据、翻译来源、时间戳、可播放媒体和完整性。
7. 预览 helper 输出后才允许原地替换。
8. 对逐字稿运行 `audit`，确认结果仍是 Raw。

## 逐字稿底线

```markdown
## 精细中英对照（按视频时间戳）

【00:00】中文阅读层。

**English:** Preserved English evidence only.
```

可见时间戳只放中文行。每条英文证据恰好保留一次。无法完成全文时记录精确终点，不宣称完整。

## 最终回复

报告目标文件、模式、中文来源、结构与 metadata 变化、原始证据和媒体嵌入、audit 结果、剩余不确定性和未来 ingest 风险。


## 证据与工具限制

采集入口 acquisition_method、转写来源 transcript_source、字幕生成方式 caption_generated、中文来源 translation_note 与人工 reviewed 分开记录，不能相互代替。
公开抓取只在明确授权且工具可用时进行；按 video_id/规范 URL 查重，访问限制或缺完整证据时停止依赖处理。不内置下载器或自动抓取服务。
多条中文共享一组英文时，不强制行数相等，不写假 English 占位行。逐条对照来源，audit 只证明结构检查通过。
原地替换会覆盖 marker 到文件末尾；先保留原件、检查尾部和差异，明确批准后才用 --in-place。不得用本脚本删除未知尾部内容。
