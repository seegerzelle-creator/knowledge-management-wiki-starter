# Raw Library Note Format

目标是保留来源，同时让资料适合阅读、复核和未来 ingest。

## Frontmatter

```yaml
---
type: raw
source_kind: external
status: raw
title: "作者或频道 - 中文可读标题"
source_title: "Original Source Title"
source_url: "https://example.com"
author:
published:
captured_at:
acquisition_method: unknown
processed_at:
source_medium: article
raw_format: article
language:
  - zh
tags:
  - clippings
  - raw-library
reviewed: false
completeness:
transcript_source:
translation_note:
related_raw: []
---
```

未知日期、作者和 URL 不要猜。处理后文件名、frontmatter `title` 和 H1 对齐。Raw 不使用 `domains`、`use_cases`、`key_points`、`evidence`、Concept 或 Synthesis 候选字段。

## 标准正文

```markdown
# 中文可读标题

## 馆藏信息

- 原始标题：
- 作者 / 来源：
- 来源链接：
- 发布日期：
- 捕捉日期：
- 内容类型：
- 原始形态：
- 处理状态：

## 读前说明

- 这是什么：
- 适合怎么读：
- 查证提醒：

## 目录 / 时间轴

- 

## 版本与质量说明

- 来源：
- 翻译说明：
- 缺陷与不确定性：

# 正文 / 逐字稿
```

读前说明是阅读脚手架，不是来源摘要。

## 视频

可播放来源保留：

```markdown
## 原始视频描述与链接

![](https://www.youtube.com/watch?v=example)

原视频描述：

> ...
```

frontmatter `source_url` 与正文嵌入保持一致。

## 逐字稿

- 中文阅读层在上，英文证据在下。
- 可见时间戳只放中文行。
- 短字幕可以按完整句、问答、例子或小论证分组，但不跨说话人或主题。
- 用户提供中文稿时保留用户措辞，并标明 provenance。
- 自主翻译时保留不确定性、限定词、语气和作者风格。
- 不能对应的中文摘要或改写文章不标为 `bilingual_transcript`。
- 处理完成后运行 helper `audit`。

## 提示词

提示词是可执行证据。英文执行版在前，中文说明在后；不改写变量、占位符、schema key 或代码块。


采集入口、转写来源、自动字幕、翻译来源与人工 reviewed 分开记录；未知不猜。用户译文不是 AI 生成。详见 Rules/raw-rules.md。只改 metadata 必须核对正文哈希。
