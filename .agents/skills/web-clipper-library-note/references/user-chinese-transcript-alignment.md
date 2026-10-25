# 用户提供中文逐字稿的对齐流程

## 目标

把用户中文稿作为主要阅读层，英文来源作为验证证据：

```markdown
【00:00】用户提供的中文逐字稿。

**English:** Preserved English evidence only.
```

## 解析

- 从第一条时间戳中文行开始，忽略附件说明前缀。
- 保留时间戳粒度、措辞和意义。
- 时间戳后的续行属于同一中文块。
- 不重译、不润色、不自动补齐。

## 对齐

- 优先按时间区间，再按语义顺序。
- 一个中文块可以对应多个短英文片段。
- 多个中文块共享一条较大英文证据时，把证据放在对应时间块；其他中文承接行不生成英文占位行。
- 每条英文证据必须保留一次；无法放置时标明不确定性。

中文行与英文行数量可以不同；人工对照原始英文确认每条证据出现一次，不以行数相等代替完整性。

## Metadata

```yaml
raw_format: bilingual_transcript
language:
  - en
  - zh
completeness: user_chinese_transcript_with_grouped_english_evidence_alignment
translation_note: "Chinese transcript provided by the user; Codex only aligned it with preserved English evidence and lightly normalized formatting."
```

完成前运行 `audit`，并确认来源说明不再声称中文由 Codex 翻译。

