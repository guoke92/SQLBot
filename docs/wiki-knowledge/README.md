# wiki-knowledge

本目录只保留 **仍在用的提取输入**：

- `pplatform/req-index/` — L1 文档概念源
- 契约与现行语料工作区在 [`docs/wiki/`](../wiki/README.md)（`v2`=L0+IR，`v3`=L1 draft）

历史语料 / 方案 MD / substrate / embeddings-cache / 旧 `wiki-pages*` 等已按原路径迁到仓库根目录 **`.tmp/`**（例如 `.tmp/docs/wiki-knowledge/pplatform/wiki-pages`）。

问数运行时召回走 **DB 语料库 + 向量**（`wiki_corpus` / binding），不依赖本地 `wiki-pages` 目录。本地目录仅作管理端「导入语料」默认源；当前默认改为 `docs/wiki/v3`。
