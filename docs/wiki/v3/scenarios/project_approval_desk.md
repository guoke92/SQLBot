---
type: scenario
title: 项目上线审批工作台
page_key: project_approval_desk
belong: scenarios
domain: tenant
status: draft
sources: ['code_path:l1_intermediate']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_project_approval, tenant_project_approval_flow]
---

# 项目上线审批工作台

项目上线审批工作台

```ground:scenario
scenario: project_approval_desk
hubs:
- table: tenant_project_approval
  role: master
- table: tenant_project_approval_flow
  role: flow_nodes
lifecycle:
- dict: tenant_project_approval__wf_status
  process: tenant_project_approval__wf_status
```

## 页面链接

- [[tables/tenant_project_approval]]
- [[tables/tenant_project_approval_flow]]
- [[dicts/tenant_project_approval__wf_status]]
- [[processes/tenant_project_approval__wf_status]]
