---
type: dict
title: cust_group_rel.cust_type
page_key: cust_group_rel__cust_type
belong: dicts
status: draft
anchors: [cust_group_rel.cust_type]
sources: ['database_profile:cust_group_rel.cust_type']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [cust_group_rel]
---

# cust_group_rel.cust_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_group_rel.cust_type`，表页 [[tables/cust_group_rel]]。

## 取值

```ground:dict
dict: cust_group_rel__cust_type
fields: [cust_group_rel.cust_type]
values:
  '["CORE"]': {trust: proposed}
  '["CORPORATION_COMPANY"]': {trust: proposed}
  '["SUPPLIER"]': {trust: proposed}
  '["CORPORATION_COMPANY","SUPPLIER"]': {trust: proposed}
  '["CORE","CORPORATION_COMPANY"]': {trust: proposed}
  '["FINANCE"]': {trust: proposed}
  '["CORPORATION_COMPANY","FINANCE"]': {trust: proposed}
  '["PROJECT_COMPANY"]': {trust: proposed}
  '["DEALER"]': {trust: proposed}
  '["CORE","CORPORATION_COMPANY","SUPPLIER"]': {trust: proposed}
  '["CORPORATION_COMPANY","PROJECT_COMPANY"]': {trust: proposed}
  '["CORPORATION_COMPANY","CORE"]': {trust: proposed}
  '["CORPORATION_COMPANY","CORE","SUPPLIER"]': {trust: proposed}
  '["CORE","CORPORATION_COMPANY","FINANCE"]': {trust: proposed}
  '["CORPORATION_COMPANY","PLATFORM_OPERATOR_COMPANY"]': {trust: proposed}
  '["CORPORATION_COMPANY","FINANCE","PLATFORM_OPERATOR_COMPANY"]': {trust: proposed}
  '["CORE","CORPORATION_COMPANY","PLATFORM_OPERATOR_COMPANY"]': {trust: proposed}
  '["CORPORATION_COMPANY","SUPPLIER","PROJECT_COMPANY"]': {trust: proposed}
  '["CORPORATION_COMPANY","CORE","FINANCE"]': {trust: proposed}
  '["CORPORATION_COMPANY","SUPPLIER","CORE"]': {trust: proposed}
  '["CORE","CORPORATION_COMPANY","PROJECT_COMPANY"]': {trust: proposed}
  '["CORPORATION_COMPANY","PROJECT_COMPANY","SUPPLIER","FINANCE"]': {trust: proposed}
  '["CORPORATION_COMPANY","PROJECT_COMPANY","SUPPLIER"]': {trust: proposed}
triage: keep
```
