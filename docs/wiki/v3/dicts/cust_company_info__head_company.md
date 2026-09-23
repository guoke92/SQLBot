---
type: dict
title: cust_company_info.head_company
page_key: cust_company_info__head_company
belong: dicts
status: draft
anchors:
- cust_company_info.head_company
sources:
- database_profile:cust_company_info.head_company
- agent:hold_promote
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related:
- cust_company_info
---
# cust_company_info.head_company

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 复审 promote：二元/开关码 + LLM 中文 label。
物理列 `cust_company_info.head_company`，表页 [[tables/cust_company_info]]。

## 取值

```ground:dict
dict: cust_company_info__head_company
fields:
- cust_company_info.head_company
values:
  Y:
    trust: proposed
    label: 是
  N:
    trust: proposed
    label: 否
triage: keep
```
