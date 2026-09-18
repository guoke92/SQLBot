---
type: dict
title: tenant_project_approval_flow_config.node_name
page_key: tenant_project_approval_flow_config__node_name
belong: dicts
status: draft
anchors: [tenant_project_approval_flow_config.node_name]
sources: ['database_profile:tenant_project_approval_flow_config.node_name']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [tenant_project_approval_flow_config]
---

# tenant_project_approval_flow_config.node_name

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `tenant_project_approval_flow_config.node_name`，表页 [[tables/tenant_project_approval_flow_config]]。

## 取值

```ground:dict
dict: tenant_project_approval_flow_config__node_name
fields: [tenant_project_approval_flow_config.node_name]
values:
  方案配置: {trust: proposed}
  其他: {trust: proposed}
  方案经理: {trust: proposed}
  运营审批: {trust: proposed}
  业务经理审批: {trust: proposed}
  法务复核: {trust: proposed}
  法务经办: {trust: proposed}
triage: keep
```
