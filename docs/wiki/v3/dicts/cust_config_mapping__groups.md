---
type: dict
title: cust_config_mapping.groups
page_key: cust_config_mapping__groups
belong: dicts
status: draft
anchors: [cust_config_mapping.groups]
sources: ['database_profile:cust_config_mapping.groups']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_config_mapping]
---

# cust_config_mapping.groups

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `cust_config_mapping.groups`，表页 [[tables/cust_config_mapping]]。

## 取值

```ground:dict
dict: cust_config_mapping__groups
fields: [cust_config_mapping.groups]
values:
  BRANCH_COMPANY: {trust: proposed}
  HEAD_COMPANY: {trust: proposed}
triage: hold
needs_review: true
```
