---
name: clarify-raw-captures
description: Save and clarify Raw/Captures notes without replacing the user's thinking. Use for `Capture：`, `仅保存 Capture：`, fragments, questions, observations, hypotheses, voice-to-text notes, unfiltered AI responses, or loose conversation excerpts. Preserve the original record, confirm the original context before understanding previews or semantic searches, and do not create mature Wiki conclusions by default.
---

# 临时捕捉澄清化

把临时捕捉变成未来可以继续思考的入口，不替用户把问题想完。

## 核心边界

- 只处理 `Raw/Captures/` 和明确指定的临时捕捉。
- 不覆盖、删减、润色、重排或改写原始记录。
- `Capture：` 授权原样创建文件、回读验证并进入背景确认。
- `仅保存 Capture：` 授权创建并回读验证后停止。
- 其他隐式触发默认只在对话中预览。
- 只有用户确认后才追加 `## 理解对齐版`。
- 不自动创建 Source、Seed、Concept、Synthesis 或 Output。
- 涉及身份、医疗、财务、客户资料或公司机密时，停止写入并确认边界。

## 必须读取

1. `AGENTS.md`
2. `Rules/raw-rules.md`
3. 保存和等待背景阶段不预读理解模板。背景确认后才读取 `references/capture-alignment-format.md`。

背景和理解确认后，判断知识出口时继续读取 `references/capture-exit-routing.md`。要求摄取进 Wiki 时，切换到项目 ingest 工作流。

## 主流程

1. 识别是对话落盘、仅保存、理解预览、确认追加、继续推演还是批量分诊。
2. 明确落盘时，检查同名和重复正文；完全重复返回已有文件，同名不同内容使用日期或序号消歧。
3. 仅在有明确保存授权时，把前缀后的正文原样写入 `Raw/Captures/`，不自动增加 H1 或 frontmatter，并回读验证。已有文件只读，无保存授权不创建文件。
4. 仅保存入口在第 3 步后立即停止。其他入口先询问并确认原始前提、背景、上下文和对象；本轮已提供也要复述请其确认。未回答前不预览、不搜索近义 Seed、不判断出口。随后判断 Capture 类型：question、idea、observation、hypothesis、connection、tension、voice transcript 或 AI / conversation fragment。
5. 按参考生成轻量或标准理解预览，区分用户原意、AI 解释和待确认推断。
6. 最多提出 3 个会实质改变理解的问题。
7. 未确认时停止；确认后只追加对齐版，不覆盖原文。
8. 给出一个主要出口和最多一个次要出口。

## 继续推演

只有用户明确要求分析、回答或推演时才执行，并使用：

```markdown
### AI 暂定分析

以下内容是 Codex 的当前推演，不是用户原始观点，也不是已经确认的 Wiki 结论。
```

默认留在对话中；需要写入时另行确认。

## 最终回复

报告处理模式、文件、回读验证、原文是否保持不变、当前确认状态、主要知识出口和仍需确认的动作。


批量先列完整清单，再逐篇确认背景；已有理解版同样适用。仅保存最终回复只报告文件和回读验证；背景关口阶段只报告保存结果并询问背景，不输出知识出口。
