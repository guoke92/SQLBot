---
type: dict
title: cust_project_rel.project_open_status
page_key: cust_project_rel__project_open_status
belong: dicts
status: draft
anchors: [cust_project_rel.project_open_status]
sources: ['database_profile:cust_project_rel.project_open_status']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_project_rel]
---

# cust_project_rel.project_open_status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_project_rel.project_open_status`，表页 [[tables/cust_project_rel]]。

## 取值

```ground:dict
dict: cust_project_rel__project_open_status
fields: [cust_project_rel.project_open_status]
values:
  NOT_OPEN: {trust: proposed}
  OPENED: {trust: proposed}
triage: keep
```
