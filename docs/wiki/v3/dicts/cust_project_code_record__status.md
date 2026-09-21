---
type: dict
title: cust_project_code_record.status
page_key: cust_project_code_record__status
belong: dicts
status: draft
anchors: [cust_project_code_record.status]
sources: ['database_profile:cust_project_code_record.status']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_project_code_record]
---

# cust_project_code_record.status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_project_code_record.status`，表页 [[tables/cust_project_code_record]]。

## 取值

```ground:dict
dict: cust_project_code_record__status
fields: [cust_project_code_record.status]
values:
  Y: {trust: proposed}
  N: {trust: proposed}
triage: keep
```
