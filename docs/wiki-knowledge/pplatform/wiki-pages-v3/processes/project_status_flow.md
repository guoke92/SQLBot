---
type: process
title: 租户项目状态机
page_key: project_status_flow
domain: 租户产品/互通产品/租户项目
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: processes
field_targets:
  - tenant_project.project_status
---

创建为 `'0'`；生效 `'1'`；失效 `'2'`。上线审批通过走 effective。

```ground:process
name: 租户项目状态机
field: tenant_project.project_status
states:
  - value: 0
    label: 待生效
    source: code_enum
  - value: 1
    label: 已生效
    source: code_enum
  - value: 2
    label: 已失效
    source: code_enum
transitions:
  - from: 0
    event: 项目生效
    to: 1
    evidence: "code_path:TenantProjectDomainService.java:234"
  - from: 1
    event: 项目失效
    to: 2
    evidence: "code_path:TenantProjectDomainService.java:225"
```
