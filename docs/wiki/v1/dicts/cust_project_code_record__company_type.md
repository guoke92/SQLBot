---
type: dict
title: cust_project_code_record.company_type
page_key: cust_project_code_record__company_type
belong: dicts
status: draft
anchors: [cust_project_code_record.company_type]
sources: ['database_profile:cust_project_code_record.company_type']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [cust_project_code_record]
---

# cust_project_code_record.company_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认（测库单值不构成排除依据）。
物理列 `cust_project_code_record.company_type`，表页 [[tables/cust_project_code_record]]。

## 取值

```ground:dict
dict: cust_project_code_record__company_type
fields: [cust_project_code_record.company_type]
values:
  '["SUPPLIER"]': {trust: proposed}
  '["FINANCE","SUPPLIER"]': {trust: proposed}
  '["CORE","SUPPLIER","DEALER"]': {trust: proposed}
  '["CORE","SUPPLIER"]': {trust: proposed}
  '["PROJECT_COMPANY","CORE"]': {trust: proposed}
  '["PROJECT_COMPANY","DEALER"]': {trust: proposed}
  '["CORE_MANAGER"]': {trust: proposed}
  '["PROJECT_COMPANY"]': {trust: proposed}
  '["CORPORATION_COMPANY","SUPPLIER"]': {trust: proposed}
  '["SUPPLIER","PROJECT_COMPANY"]': {trust: proposed}
  '["CORE"]': {trust: proposed}
  '["SUPPLIER","DEALER","CORE"]': {trust: proposed}
  '["CORPORATION_COMPANY","CORE","SUPPLIER"]': {trust: proposed}
triage: hold
needs_review: true
```
