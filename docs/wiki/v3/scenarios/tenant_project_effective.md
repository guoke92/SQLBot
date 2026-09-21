---
type: scenario
title: 生效租户项目
page_key: tenant_project_effective
belong: scenarios
domain: tenant
status: draft
sources: ['code_path:l1_intermediate']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_project]
---

# 生效租户项目

生效租户项目

```ground:scenario
scenario: tenant_project_effective
hubs:
- table: tenant_project
  role: master
lifecycle:
- dict: tenant_project__project_status
  process: tenant_project__project_status
```

## 页面链接

- [[tables/tenant_project]]
- [[dicts/tenant_project__project_status]]
- [[processes/tenant_project__project_status]]
