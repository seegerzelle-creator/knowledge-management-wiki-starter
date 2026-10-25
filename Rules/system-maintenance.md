---
type: rule
status: active
description: >
  修改 AGENTS、Rules、Schema、Blueprint、Templates、Skills、index、log 或讨论 RAG、自动化和外部平台时使用。
---

# System Maintenance

## 继续读取

- 涉及未来扩建读取 `Blueprint.md`。
- 涉及字段和页面类型读取 `Schema.md`。
- 涉及 Skills 检查 `Skills.md` 与 `.agents/skills/`。
- 涉及 lint 读取 `Rules/lint-review.md`。
- 读取失败时停止依赖该文件的结构性写入。

## 微计划

多文件或结构性任务先给 2-5 步计划，按阶段执行，不越过确认关口。完成后更新 `index.md` 与 `log.md`。

## 扩建检查

当用户提到 RAG、Assets、Comparison、Skills、内容生产、自动化、抓取、同步或外部平台时，按 Blueprint 报告：

```text
- 模块：
- 当前状态：
- 触发信号：
- 是否达标：
- 建议动作：
- 是否需要确认：
```

达到触发条件只代表可以提出方案，不代表可以自动实施。

## 结构边界

- `AGENTS.md` 保持入口、红线、路由和读取失败处理。
- 细节进入 `Rules/`。
- `Raw/` 保存证据，`Wiki/` 保存编译知识。
- `ThinkDesk.md` 保存当前待审批事项。
- `.agents/skills/` 保存稳定、重复、边界清楚的工作流。

## 必须确认

- 新增、重命名或删除顶层知识目录。
- 改变 Schema 或正式 domains。
- 批量重写规则、模板或页面。
- 创建新 Skill。
- 引入 RAG、数据库、同步、自动化、云模型、付费 API 或外部平台。


## 授权复用与分发边界

已有具体预览批准且范围未变，直接完成授权修改和验证，不重复询问。出现实质变化时只核对变化部分；明确要求先展示具体产物后批准的关口不可跳过。
只读检查不写 index/log/ThinkDesk；已授权系统维护才同步必要导航。
AGENTS 只承载入口、红线、路由和读取失败处理，细节放 Rules。Skill 内容按实际需要读取，不因关键词强行启动额外流程。
公开模板只携带 .example.md 个人文件模板。不要把自己的 USER-CONTEXT、Raw/Wiki、日志、审批或旧库整体覆盖进公共仓库。
