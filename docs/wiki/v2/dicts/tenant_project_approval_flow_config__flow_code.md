---
type: dict
title: tenant_project_approval_flow_config.flow_code
page_key: tenant_project_approval_flow_config__flow_code
belong: dicts
status: draft
anchors: [tenant_project_approval_flow_config.flow_code]
sources: ['database_profile:tenant_project_approval_flow_config.flow_code']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [tenant_project_approval_flow_config]
---

# tenant_project_approval_flow_config.flow_code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `tenant_project_approval_flow_config.flow_code`，表页 [[tables/tenant_project_approval_flow_config]]。

## 取值

```ground:dict
dict: tenant_project_approval_flow_config__flow_code
fields: [tenant_project_approval_flow_config.flow_code]
values:
  REGULAR: {trust: proposed}
  STANDARD: {trust: proposed}
  NO_ONLINE: {trust: proposed}
triage: hold
needs_review: true
```
