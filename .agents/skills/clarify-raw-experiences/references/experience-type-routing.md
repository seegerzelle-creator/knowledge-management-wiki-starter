# Experience 类型路由

## 输入形态

| 值 | 含义 | 重点 |
|---|---|---|
| `firsthand_narrative` | 直接叙述亲历事件 | 保留原话，区分行为和解释 |
| `memory_reconstruction` | 事后凭记忆补写 | 标记记忆边界 |
| `conversation_excerpt` | 部分对话 | 说明上下文不完整 |
| `structured_digest` | 已整理摘要 | 审计来源与状态，避免重复编译 |
| `mixed` | 多种材料混合 | 分区标记证据层 |

## 模式选择

- “发生了什么、做了什么、结果怎样” -> 事件复盘。
- “为什么形成这个判断、如何验证” -> 判断形成。
- 已有对齐版、下游页面或过期状态 -> 既有记录维护。
- 多文件第一轮 -> 批量分诊，不批量写入。

## 特殊路由

- 外部作者材料 -> `Raw/External/`。
- 临时问题和灵感 -> `Raw/Captures/`。
- 已成文作品 -> `Raw/Outputs/`。
- 明确要求进入 Wiki -> 切换 guided ingest。

