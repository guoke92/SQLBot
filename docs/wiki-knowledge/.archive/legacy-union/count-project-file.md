---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:project-file@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 项目文件有多少
page_key: count-project-file
domain: 项目管理
anchors:
- project_file_info
---
# 项目文件有多少

问法：项目文件有多少

```ground:pattern
pattern: count-project-file
question: 项目文件有多少
sql: SELECT COUNT(DISTINCT id) AS cnt FROM project_file_info WHERE enable = 'Y'
verification: PENDING_VALIDATION
```

## 关联
- [[project_file_info]]
