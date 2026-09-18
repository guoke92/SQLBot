---
type: dict
title: cust_project_code_record.type
page_key: cust_project_code_record__type
belong: dicts
status: draft
anchors: [cust_project_code_record.type]
sources: ['database_profile:cust_project_code_record.type']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [cust_project_code_record]
---

# cust_project_code_record.type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_project_code_record.type`，表页 [[tables/cust_project_code_record]]。

## 取值

```ground:dict
dict: cust_project_code_record__type
fields: [cust_project_code_record.type]
values:
  userCompanyRegister: {trust: proposed}
  产品中心-企业认证成功: {trust: proposed}
  产品中心: {trust: proposed}
  PC_BUILD: {trust: proposed}
triage: keep
```
