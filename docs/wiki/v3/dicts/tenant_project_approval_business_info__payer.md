---
type: dict
title: tenant_project_approval_business_info.payer
page_key: tenant_project_approval_business_info__payer
belong: dicts
status: draft
anchors: [tenant_project_approval_business_info.payer]
sources: ['database_profile:tenant_project_approval_business_info.payer']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [tenant_project_approval_business_info]
---

# tenant_project_approval_business_info.payer

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `tenant_project_approval_business_info.payer`，表页 [[tables/tenant_project_approval_business_info]]。

## 取值

```ground:dict
dict: tenant_project_approval_business_info__payer
fields: [tenant_project_approval_business_info.payer]
values:
  SUPPLIER: {trust: proposed}
  融资申请人: {trust: proposed}
  CORE: {trust: proposed}
  资金方: {trust: proposed}
  APPLICANT: {trust: proposed}
triage: keep
```
