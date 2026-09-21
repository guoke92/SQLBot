---
type: caliber
title: 已生效租户项目
page_key: effective_tenant_project
belong: calibers
domain: tenant
status: draft
field_targets: [tenant_project.project_status, tenant_project.enable]
sources: ['code_path:TenantProjectDaoImpl.java:35']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_project]
---

# 已生效租户项目

回答「当前有效项目」。待生效 0、已失效 2 都不算。不要用审批 wf_status=FINISHED 代替。

```ground:caliber
caliber: 已生效租户项目
field_targets: [tenant_project.project_status, tenant_project.enable]
predicate: tenant_project.project_status = '1' AND tenant_project.enable = 'Y'
scope: global
boundary: 回答「当前有效项目」。待生效 0、已失效 2 都不算。不要用审批 wf_status=FINISHED 代替。
using_relations: []
evidence: code_path:TenantProjectDaoImpl.java:35
```

## 页面链接

- [[tables/tenant_project]]
- [[dicts/tenant_project__enable]]
- [[dicts/tenant_project__project_status]]
- [[processes/tenant_project__project_status]]
