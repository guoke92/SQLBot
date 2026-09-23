---
type: dict
title: cust_company_info.need_register_bs
page_key: cust_company_info__need_register_bs
belong: dicts
status: draft
anchors:
- cust_company_info.need_register_bs
sources:
- database_profile:cust_company_info.need_register_bs
- database_schema:cust_company_info.need_register_bs
- code_path:OpenStatus.java:20
- agent:hold_promote_code
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related:
- cust_company_info
---
# cust_company_info.need_register_bs

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。 复审 promote：OpenStatus enum: Y已开通/P开通中/N未开通；业务口语「是否需要开通上上签」，P 来自 OpenStatus 复用。
物理列 `cust_company_info.need_register_bs`，表页 [[tables/cust_company_info]]。

## 取值

```ground:dict
dict: cust_company_info__need_register_bs
fields:
- cust_company_info.need_register_bs
values:
  N:
    trust: proposed
    label: 未开通/不需要
  Y:
    trust: proposed
    label: 需要开通
  P:
    trust: proposed
    label: 开通中
triage: keep
evidence: 'OpenStatus enum: Y已开通/P开通中/N未开通；业务口语「是否需要开通上上签」，P 来自 OpenStatus 复用。'
```
