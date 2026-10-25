---
type: rule
status: active
description: >
  对知识库做只读 lint、健康检查和维护建议。不自动批量删除、合并或重构。
---

# Lint Review

## 继续读取

- 始终读取 `Schema.md`。
- 发现冲突或过时判断时读取 `Rules/knowledge-maintenance.md`。
- 发现扩建信号时读取 `Blueprint.md` 与 `Rules/system-maintenance.md`。
- 读取失败时只报告可安全确认的部分。

## 检查范围

- Raw 是否有来源缺失、重复或敏感泄露。
- 需要编译且未标记 `raw_only` 的材料是否长期未处理。
- Wiki frontmatter 是否符合页面类型。
- `domains` 是否只使用正式值。
- Seed 是否有 `next_action`。
- Concept 是否有定义、例子、反例、边界和来源。
- Synthesis 是否有具体问题、独立证据、冲突与不确定性。
- active Concept / Synthesis 是否仍为 `reviewed: false`。
- 是否存在断链、孤立、重复、过时或证据族误计。

## 输出

```text
- 范围：
- 通过：
- 问题：
- 风险等级：
- 可直接修复：
- 需要确认：
- 建议下一步：
```

检查结果先报告，不自动批量删除、合并或重构。高影响事项可建议进入 `ThinkDesk.md`；只读请求不写入。


## 状态一致性补充

检查 Source 的“下一步”是否仍列已完成动作，Experience 的历史待办是否已由追加记录解释，ingest_disposition 是否与真实下游一致。
只读检查只在对话提出 ThinkDesk 候选，不写入任何文件；获准维护时才登记。raw_only 不属于漏处理。
