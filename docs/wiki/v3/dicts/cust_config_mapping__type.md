---
type: dict
title: cust_config_mapping.type
page_key: cust_config_mapping__type
belong: dicts
status: draft
anchors: [cust_config_mapping.type]
sources: ['database_profile:cust_config_mapping.type']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [cust_config_mapping]
---

# cust_config_mapping.type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_config_mapping.type`，表页 [[tables/cust_config_mapping]]。

## 取值

```ground:dict
dict: cust_config_mapping__type
fields: [cust_config_mapping.type]
values:
  COMPANY_TYPE_MAPPING: {trust: proposed}
  COMPANY_MEDIA: {trust: proposed}
  CHANGE_ITEM: {trust: proposed}
triage: keep
```
