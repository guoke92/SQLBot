---
type: dict
title: tenant_project_approval_flow_credit.is_group_limit
page_key: tenant_project_approval_flow_credit__is_group_limit
belong: dicts
status: draft
anchors: [tenant_project_approval_flow_credit.is_group_limit]
sources: ['database_profile:tenant_project_approval_flow_credit.is_group_limit']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [tenant_project_approval_flow_credit]
---

# tenant_project_approval_flow_credit.is_group_limit

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `tenant_project_approval_flow_credit.is_group_limit`，表页 [[tables/tenant_project_approval_flow_credit]]。

## 取值

```ground:dict
dict: tenant_project_approval_flow_credit__is_group_limit
fields: [tenant_project_approval_flow_credit.is_group_limit]
values:
  Y: {trust: proposed}
  N: {trust: proposed}
triage: hold
needs_review: true
```
