---
type: process
title: 租户项目状态
page_key: tenant_project__project_status
belong: processes
domain: tenant
status: draft
anchors: [tenant_project.project_status]
field_targets: [tenant_project.project_status]
sources: ['code_path:TenantProjectDomainService.java:169', 'code_path:TenantProjectDomainService.java:235',
  'code_path:TenantProjectDomainService.java:226']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_project]
---

# 租户项目状态

钉 tenant_project.project_status。创建写 0 待生效；生效写 1；失效写 2（枚举名 INVLIAD）。
人工 /tenantProject/effective 与审批 FINISHED 都写 1。重新发起审批会对已生效项目先写 2。
不要把 wf_status 当成项目是否生效。


```ground:process
process: 租户项目状态
field: tenant_project.project_status
entry: POST /app-web/tenantProject/create
stages:
- stage: 创建
  transitions:
  - from: '0'
    event: TenantProjectDomainService.create
    to: '0'
    evidence: code_path:TenantProjectDomainService.java:169
- stage: 生效
  transitions:
  - from: '0'
    event: effective / 审批通过
    to: '1'
    evidence: code_path:TenantProjectDomainService.java:235
- stage: 失效
  transitions:
  - from: '1'
    event: invalid
    to: '2'
    evidence: code_path:TenantProjectDomainService.java:226
```

## 页面链接

- [[tables/tenant_project]]
- [[dicts/tenant_project__project_status]]
