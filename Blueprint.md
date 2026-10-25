---
type: system_blueprint
status: active
created: 2026-07-25
updated: 2026-07-25
---

# Blueprint

本文件记录未来可能扩建的方向、触发条件和确认边界。它不替代当前 `AGENTS.md`、`Rules/` 或 `Schema.md`。

## 扩建顺序

```text
资料摄取
-> Wiki 编译
-> Synthesis 判断
-> 检索增强
-> 可复用工作流
-> 内容生产
-> 自动化
-> 外部发布
```

不要跳过判断层直接自动化。

## 状态

- `active`：已经启用。
- `watch`：出现信号，继续观察。
- `ready_to_propose`：条件基本满足，应提出方案。
- `ready_to_build`：用户已确认，可以实施。
- `not_ready`：当前不需要。

## 当前主建筑

状态：`active`

```text
Raw -> Wiki -> Schema
```

当前优先稳定资料摄取、页面质量、链接和综合判断，不继续增加顶层目录。

## Domain / Tag

状态：`watch`

当同一候选领域在多篇页面中反复出现，且无法由现有 domains 或 tags 覆盖时，提出正式 domain 变更方案。正式变更必须确认。

## 用途专属知识库

状态：`watch`

当同一 `use_cases` 反复出现，并且主 Wiki 与某个具体用途互相干扰时，优先用索引、标签或导出包解决；新增目录或独立库必须确认。

## Assets

状态：`watch`

图片、PDF、音频等附件明显增多并影响查找时，再提出附件层方案。创建目录和迁移附件必须确认。

## Comparison

状态：`watch`

比较类内容优先放入 `Wiki/synthesis/` 并使用标签。只有数量明显增长时才讨论子目录。

## RAG

状态：`not_ready`

当 Wiki 页面约超过 150 篇、Source 约超过 50 篇、跨页检索明显吃力且 metadata 稳定时，提出本地、插件或数据库方案比较。不得自动引入向量数据库、embedding、云模型或付费服务。

## Skills

状态：`watch`

同一流程反复出现、边界稳定且需要一句短指令触发时，可以提出新的项目级 Skill。创建或安装前必须确认。

## Content Engine

状态：`watch`

内容生产应优先从成熟 Concept、Synthesis 和已筛选材料生成，不直接从 Raw 自动发布。正式发布前必须确认。

## Automation

状态：`not_ready`

只有当流程反复出现、来源和隐私边界清楚、失败不会破坏 Raw 或误发布时，才提出自动化方案。先自动生成提醒或候选，不自动写结论或发布。

## External Publishing

状态：`not_ready`

连接任何外部平台前，先设计字段、目录、权限、版本和失败处理；从人工确认后的草稿导出开始。

## Technical Infrastructure

状态：`not_ready`

数据库、同步、备份、云模型、付费 API 和额外权限只在明确需求出现后讨论，不为未来复杂度提前建设。

## 检查格式

```text
- 模块：
- 当前状态：
- 触发信号：
- 是否达标：
- 建议动作：
- 是否需要用户确认：
```

