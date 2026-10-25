# 逐字稿模式路由

## 模式 A：Codex 自主翻译

条件：有英文证据、没有同源中文稿、用户需要中文阅读版。

1. 提取英文证据和章节。
2. 建立术语、人物、风格和 ASR 疑点清单。
3. 完整句段使用一对一 TSV；短碎片使用语义分组。
4. 对照终审后才原地写入。

常用命令：

```bash
python3 .agents/skills/web-clipper-library-note/scripts/bilingual_transcript_tool.py extract Raw/External/example.md
python3 .agents/skills/web-clipper-library-note/scripts/bilingual_transcript_tool.py check-table Raw/External/example.md translations.tsv
python3 .agents/skills/web-clipper-library-note/scripts/bilingual_transcript_tool.py render Raw/External/example.md translations.tsv
python3 .agents/skills/web-clipper-library-note/scripts/bilingual_transcript_tool.py align-generated-cn Raw/External/example.md generated-cn.txt
```

## 模式 B：用户中文稿对齐

条件：用户提供同源、同顺序的中文逐字稿。

- 保留用户措辞和时间戳粒度。
- 一对一时使用 TSV；合并或跳段时使用 `align-user-cn`。
- 不自动重新翻译或补齐缺失中文。
- metadata 明确写“Chinese transcript provided by the user”。

## 模式 C：已有双语维护

检查中英文数量、顺序、时间戳、metadata 和证据完整性。保留有效译文，只修缺漏、错位和格式。多次运行应幂等。

## 完成检查

- metadata 与正文一致。
- 中文可共享一组英文证据，不强制行数相等；保全每条原始英文证据，不造占位行。
- 英文证据行无可见时间戳。
- 每条英文证据保留一次。
- 视频嵌入、URL 和原始标题保留。
- 文件名、title 与 H1 对齐。
- `audit` 返回成功，否则不宣称完成。


Helper 的 audit 只检查结构和部分 metadata，不能证明语义对齐、翻译质量或原始证据完整性。必须与原始来源逐条核对。--in-place 会替换 marker 到文件末尾；先保留原件、预览差异，若尾部有其他内容不要直接使用。所有 helper 默认仅预览 stdout，不自动改 metadata。
