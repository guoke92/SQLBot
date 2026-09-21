---
type: dict
title: cust_company_info.enable
page_key: cust_company_info__enable
belong: dicts
status: draft
anchors: [cust_company_info.enable]
sources: ['database_profile:cust_company_info.enable']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [cust_company_info]
---

# cust_company_info.enable

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_company_info.enable`，表页 [[tables/cust_company_info]]。

## 取值

```ground:dict
dict: cust_company_info__enable
fields: [cust_company_info.enable]
values:
  Y: {trust: proposed}
  N: {trust: proposed}
triage: keep
```
