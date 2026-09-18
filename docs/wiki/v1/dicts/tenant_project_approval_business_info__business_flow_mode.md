---
type: dict
title: tenant_project_approval_business_info.business_flow_mode
page_key: tenant_project_approval_business_info__business_flow_mode
belong: dicts
status: draft
anchors: [tenant_project_approval_business_info.business_flow_mode]
sources: ['database_profile:tenant_project_approval_business_info.business_flow_mode']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [tenant_project_approval_business_info]
---

# tenant_project_approval_business_info.business_flow_mode

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `tenant_project_approval_business_info.business_flow_mode`，表页 [[tables/tenant_project_approval_business_info]]。

## 取值

```ground:dict
dict: tenant_project_approval_business_info__business_flow_mode
fields: [tenant_project_approval_business_info.business_flow_mode]
values:
  CONFIRM_RIGHT_AFTER: {trust: proposed}
  CONFIRM_RIGHT_FIRST: {trust: proposed}
  后确权: {trust: proposed}
  先确权: {trust: proposed}
triage: keep
```
