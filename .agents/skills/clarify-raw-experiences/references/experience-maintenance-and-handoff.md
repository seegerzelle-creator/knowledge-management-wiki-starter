# Experience 维护与知识交接

## 状态校准

检查：

1. 旧“待完成”是否已经完成。
2. Wiki 页面的下一步是否已执行。
3. 新结果支持、补充、修正、挑战还是推翻原判断。
4. `status`、`reviewed`、`confidence`、`updated` 是否合理。
5. Raw 与下游页面链接是否有效。

保留历史时态；追加更新，不删除当时的待办。

## 知识出口

- `raw_only`：只留 Raw，不要求 Source Summary。
- `wiki_candidate`：可能进入 Wiki，但尚未完成 guided ingest。
- `ingested`：已经存在可追溯的编译页面。

内容丰富不等于要同时创建 Source、多个 Concept 和 Synthesis。选择最小充分结果。

## 证据独立性

同一 Raw、它的摘要、仅由它派生的 Seed、Concept 和 Synthesis 属于同一证据族。页面可以互链，但不能按数量提高置信度。

## 生命周期

- 未确认：通常 `draft + reviewed: false`。
- 已确认：可以 `active + reviewed: true`。
- `confidence` 单独表达证据强度。

