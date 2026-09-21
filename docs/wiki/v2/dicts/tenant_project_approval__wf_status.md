---
type: dict
title: tenant_project_approval.wf_status
page_key: tenant_project_approval__wf_status
belong: dicts
status: draft
anchors: [tenant_project_approval.wf_status]
sources: ['database_profile:tenant_project_approval.wf_status']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [tenant_project_approval]
---

# tenant_project_approval.wf_status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `tenant_project_approval.wf_status`，表页 [[tables/tenant_project_approval]]。

## 取值

```ground:dict
dict: tenant_project_approval__wf_status
fields: [tenant_project_approval.wf_status]
values:
  RUNNING: {trust: proposed}
  FINISHED: {trust: proposed}
  TERMINATED: {trust: proposed}
  PENDING: {trust: proposed}
  REVOKED: {trust: proposed}
triage: keep
```
