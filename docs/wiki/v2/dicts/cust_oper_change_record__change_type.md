---
type: dict
title: cust_oper_change_record.change_type
page_key: cust_oper_change_record__change_type
belong: dicts
status: draft
anchors: [cust_oper_change_record.change_type]
sources: ['database_profile:cust_oper_change_record.change_type']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [cust_oper_change_record]
---

# cust_oper_change_record.change_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_oper_change_record.change_type`，表页 [[tables/cust_oper_change_record]]。

## 取值

```ground:dict
dict: cust_oper_change_record__change_type
fields: [cust_oper_change_record.change_type]
values:
  BATCH: {trust: proposed}
  ASSET_AUDIT_SYNC: {trust: proposed}
  CUST_CHANGE_CALLBACK: {trust: proposed}
  MANUAL: {trust: proposed}
triage: keep
```
