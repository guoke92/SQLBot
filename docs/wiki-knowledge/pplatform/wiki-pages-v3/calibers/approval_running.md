---
type: caliber
title: 上线审批中
page_key: approval_running
domain: 微企链立项与项目审批
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: calibers
field_targets:
  - tenant_project_approval.wf_status
---

工作流审批中。

```ground:caliber
name: 上线审批中
predicate: "tenant_project_approval.wf_status = 'RUNNING'"
scope: tenant_project_approval
evidence: code
```
