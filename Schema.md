---
type: schema
status: active
created: 2026-07-25
updated: 2026-10-24
reviewed: false
---

# 知识库结构规范

## 核心分层

```text
Raw -> Wiki -> Schema
```

- `Raw/` 保存原始资料和个人证据，默认不改写。
- `Wiki/` 保存经过整理、可追溯、可链接的知识页面。
- `Rules/` 约束 Codex 如何工作。
- `Templates/` 规定页面最小结构。
- `ThinkDesk.md` 集中待审批维护事项。
- `.agents/skills/` 保存项目级可调用工作流。

## Raw 类型

- `Raw/External/`：外部文章、网页、书摘、论文、课程、视频、播客和文档。
- `Raw/Captures/`：问题、灵感、观察、假设、语音转文字和临时片段。
- `Raw/Experiences/`：个人经历、项目复盘、判断过程和实践反馈。
- `Raw/Outputs/`：自己的文章、草稿、报告、方案和脚本。

## Wiki 页面类型

- `source`：对应一个明确 Raw 来源，回答“这个来源讲了什么”。
- `seed`：值得追踪、但尚未成熟的问题、观察、假设、连接或张力。
- `entity`：人物、组织、产品、工具、项目、论文和框架等具体对象。
- `concept`：可跨情境复用的概念、原则、模型或方法。
- `synthesis`：围绕一个具体问题整合多份独立证据形成的当前最佳判断。

Capture 通常直接进入 Seed，不要求 Source Summary。

## 推荐字段

```yaml
type:
status:
created:
updated:
aliases:
tags:
domains:
domain_candidates:
use_cases:
reviewed:
sources:
related:
confidence:
agent_mode:
```

- `status`：`raw | draft | active | archived | delete_candidate`
- `confidence`：`low | medium | high`
- `agent_mode`：当前默认 `guided_ingest`
- `reviewed`：是否经过知识库所有者人工复核，不等于证据强度

外部来源可增加：

```yaml
source_url:
author:
published:
source_medium:
raw_format:
content_completeness:
```

Experience 与 Output 可增加：

```yaml
creation_mode: human_written | ai_assisted | ai_generated | unknown
ingest_disposition: raw_only | wiki_candidate | ingested
```

## 初始正式领域

```yaml
domains:
  - ai
  - work
  - learning
  - personal_growth
  - content_writing
  - knowledge_management
```

- `ai`：AI 技术、工具、应用和工作方式。
- `work`：职业、项目、协作、业务和组织实践。
- `learning`：学习、理解、练习、迁移和能力形成。
- `personal_growth`：习惯、状态、选择、复盘和长期变化。
- `content_writing`：素材、选题、表达、发布和传播。
- `knowledge_management`：资料摄取、知识编译、链接、调用和维护。

首启时可以提出修改，但新增、重命名或删除正式 domain 必须确认。尚未确认的候选放入 `domain_candidates`；临时主题优先使用 `tags`。

## `use_cases`

`domains` 回答“这是什么性质的知识”，`use_cases` 回答“它能用来做什么”。建议使用英文 snake_case，例如：

```yaml
use_cases:
  - design_learning_system
  - write_methodology_article
```

不要因用途不同复制页面。

## 页面关系与证据独立性

- Source 链接 Raw，并提出可能的后续出口。
- Seed 链接原始 Capture 或 Source。
- Entity、Concept 和 Synthesis 链接支撑它们的来源。
- 同一 Raw、它的摘要和仅由它派生的页面属于同一证据族，不能按页面数量算作多份独立证据。
- Synthesis 应说明支持证据、冲突证据、边界、不确定性和下一验证信号。

## 生命周期

- `raw`：尚未整理。
- `draft`：已结构化但未充分复核。
- `active`：当前可调用。
- `archived`：保留但不优先调用。
- `delete_candidate`：建议删除，必须确认后执行。

Concept 与 Synthesis 在 `reviewed: false` 时通常保持 `status: draft`。

## 质量标准

合格的 Source 区分来源事实、作者观点、AI 解释和待验证内容。  
合格的 Seed 有明确问题、保留原因和 `next_action`。  
合格的 Entity 的关键事实有来源。  
合格的 Concept 有定义、例子、反例、边界和来源。  
合格的 Synthesis 先给当前判断，并整合多份独立证据。


## v1.1 来源履历与授权说明

Raw 的 acquisition_method 区分 obsidian_web_clipper / codex_youtube_capture / user_supplied / unknown；transcript_source 说明字幕或 ASR 等来源；caption_generated 不明时不猜；translation_note 记录中文来源。不同字段不能相互替代。
Raw completeness 是原始内容覆盖说明，Wiki content_completeness 是来源摘要对材料完整性的判断。
个人 Experience 可用 raw_format: firsthand_narrative / memory_reconstruction / conversation_excerpt / structured_digest / mixed；未知创作方式保留 unknown。
Outputs 的 status、reviewed 与 confidence 分别表达作品状态、人工复核和证据强度；修改或发布不自动等于摄取完成。
标签仅作检索辅助。Rules/tagging-rules.md 未启用，不是字段校验依据。
公开模板不包含个人导航文件；运行时从对应 .example.md 创建。

## 页面类型专用字段

| 页面 | 专用字段 |
|---|---|
| source | source（单一 Raw 链接）、source_kind、source_medium、raw_format、content_completeness |
| seed | seed_type、source、source_kind、privacy、next_action |
| entity | entity_type |
| concept | concept_type |
| synthesis | question、review_after（有实际复查计划才填写） |

sources 保留支持来源列表；source/seed 的单一原始归属使用 source。空模板的未知值留空，真实页面按已知证据填写，不把模板默认值当作事实。
