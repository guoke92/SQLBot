---
type: dict
title: short_link.type
page_key: short_link__type
belong: dicts
status: draft
anchors: [short_link.type]
sources: ['database_profile:short_link.type']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [short_link]
---

# short_link.type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `short_link.type`，表页 [[tables/short_link]]。

## 取值

```ground:dict
dict: short_link__type
fields: [short_link.type]
values:
  NORMAL: {trust: proposed}
  FILE: {trust: proposed}
triage: keep
```
