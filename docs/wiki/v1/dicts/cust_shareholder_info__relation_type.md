---
type: dict
title: cust_shareholder_info.relation_type
page_key: cust_shareholder_info__relation_type
belong: dicts
status: draft
anchors: [cust_shareholder_info.relation_type]
sources: ['database_profile:cust_shareholder_info.relation_type']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [cust_shareholder_info]
---

# cust_shareholder_info.relation_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_shareholder_info.relation_type`，表页 [[tables/cust_shareholder_info]]。

## 取值

```ground:dict
dict: cust_shareholder_info__relation_type
fields: [cust_shareholder_info.relation_type]
values:
  LEGAL_PERSON: {trust: proposed}
  SENIOR_MANAGER: {trust: proposed}
triage: keep
```
