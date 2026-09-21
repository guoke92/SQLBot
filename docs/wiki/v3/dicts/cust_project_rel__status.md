---
type: dict
title: cust_project_rel.status
page_key: cust_project_rel__status
belong: dicts
status: draft
anchors: [cust_project_rel.status]
sources: ['database_profile:cust_project_rel.status']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_project_rel]
---

# cust_project_rel.status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_project_rel.status`，表页 [[tables/cust_project_rel]]。

## 取值

```ground:dict
dict: cust_project_rel__status
fields: [cust_project_rel.status]
values:
  '1': {trust: proposed}
  '0': {trust: proposed}
triage: keep
```
