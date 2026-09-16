---
type: caliber
title: 已生效租户项目
page_key: effective_tenant_project
domain: 租户产品/互通产品/租户项目
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
  - tenant_project.project_status
---

dictKey `'1'`。

```ground:caliber
name: 已生效租户项目
predicate: "tenant_project.project_status = '1'"
scope: tenant_project
evidence: code
```
