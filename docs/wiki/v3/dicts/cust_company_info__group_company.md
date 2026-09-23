---
type: dict
title: cust_company_info.group_company
page_key: cust_company_info__group_company
belong: dicts
status: draft
anchors:
- cust_company_info.group_company
sources:
- database_profile:cust_company_info.group_company
- agent:hold_promote_code
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related:
- cust_company_info
---
# cust_company_info.group_company

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 复审 promote：代码 CustCompanyInfoApplication:4296 仅认 Y→是，其余→否；UAT 现无 1，profile 残留保留。
物理列 `cust_company_info.group_company`，表页 [[tables/cust_company_info]]。

## 取值

```ground:dict
dict: cust_company_info__group_company
fields:
- cust_company_info.group_company
values:
  N:
    trust: proposed
    label: 否
  Y:
    trust: proposed
    label: 是
  '1':
    trust: proposed
    label: 否（脏数据）
triage: keep
evidence: 代码 CustCompanyInfoApplication:4296 仅认 Y→是，其余→否；UAT 现无 1，profile 残留保留。
```
