---
type: scenario
title: 项目上线审批
page_key: project_online_approval
belong: scenarios
domain: tenant
status: draft
aliases: [上线审批, 项目审批]
sources: ['code_path:l1_intermediate']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_project_approval, tenant_project, tenant_project_approval_flow]
---

# 项目上线审批

审批按项目 code 关联。创建 PENDING，发起 RUNNING，通过 FINISHED 并生效项目。
不要把 wf_status 当成 project_status。


```ground:scenario
scenario: project_online_approval
hubs:
- table: tenant_project_approval
  role: master
shared:
- table: tenant_project
  role: project
- table: tenant_project_approval_flow
  role: flow_nodes
lifecycle:
- dict: tenant_project_approval__wf_status
  process: tenant_project_approval__wf_status
- dict: tenant_project__project_status
  process: tenant_project__project_status
```

## 页面链接

- [[tables/tenant_project]]
- [[tables/tenant_project_approval]]
- [[tables/tenant_project_approval_flow]]
- [[dicts/tenant_project__project_status]]
- [[dicts/tenant_project_approval__wf_status]]
- [[processes/tenant_project__project_status]]
- [[processes/tenant_project_approval__wf_status]]
