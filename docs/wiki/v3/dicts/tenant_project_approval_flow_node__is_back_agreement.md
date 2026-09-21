---
type: dict
title: tenant_project_approval_flow_node.is_back_agreement
page_key: tenant_project_approval_flow_node__is_back_agreement
belong: dicts
status: draft
anchors: [tenant_project_approval_flow_node.is_back_agreement]
sources: ['database_profile:tenant_project_approval_flow_node.is_back_agreement']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_project_approval_flow_node]
---

# tenant_project_approval_flow_node.is_back_agreement

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `tenant_project_approval_flow_node.is_back_agreement`，表页 [[tables/tenant_project_approval_flow_node]]。

## 取值

```ground:dict
dict: tenant_project_approval_flow_node__is_back_agreement
fields: [tenant_project_approval_flow_node.is_back_agreement]
values:
  Y: {trust: proposed}
  N: {trust: proposed}
triage: hold
needs_review: true
```
