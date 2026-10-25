---
type: rule
status: active
description: >
  创建和维护 Source、Seed、Entity、Concept、Synthesis 页面。不处理 Raw 原文整理和系统扩建。
---

# Wiki Page Rules

## 继续读取

- 始终读取 `Schema.md` 和目标页面类型模板。
- 来源编译读取 `Rules/ingest-workflow.md`。
- 判断冲突读取 `Rules/knowledge-maintenance.md`。
- 读取失败时停止写入。

## 通用要求

- 每页有明确 `type`、`status`、日期、`domains`、`reviewed`、`sources`、`related` 和 `confidence`。
- 只添加有解释、引用或推理价值的链接。
- 未复核 Concept / Synthesis 通常为 `status: draft`、`reviewed: false`。
- `confidence` 依据独立来源、跨情境验证、可观察结果、反例和边界。

## Source

回答“这个来源讲了什么”。区分来源事实、作者观点、AI 解释和待验证内容，并链接唯一 Raw 来源。

## Seed

记录值得长期追踪的问题、观察、假设、连接或张力。必须有 `seed_type`、保留原因和 `next_action`。Capture 来源只摘录最短必要原句并链接完整 Raw。

## Entity

记录具体对象。关键事实必须有来源；把事实、观点、争议和用户关系分开。

## Concept

必须包含一句话定义、解决的问题、例子、反例、边界、相近概念区别、来源和可用场景。单篇来源复述或单次经验不直接升级为 Concept。

## Synthesis

必须：

1. 回答一个具体问题。
2. 先给当前判断。
3. 整合多份独立来源或多次实践。
4. 写清支持、冲突、边界、不确定性和下一验证信号。

创建正式 Synthesis 或大幅改变当前结论前先确认；待审批事项进入 `ThinkDesk.md`。

## 命名

系统路径和机器字段使用英文；人读标题优先使用中文。来源摘要使用“来源摘要 - 核心主题”。实体优先使用官方名称，别名放入 `aliases`。


## 原始背景与页面状态

Capture 必须先完成逐篇背景确认、理解预览确认，才搜索近义 Seed 或判断出口。不能从标题、当前项目或已有页面反推语境。
Concept 创建前检查定义、解决的问题、正例/反例、边界、来源、可迁移用途和近义页；不成熟则保留 Seed。
只有用户实际完成人工复核，才能写 reviewed: true；Concept/Synthesis 未复核通常为 draft，不因 AI 校验通过而升级。
