---
type: concept
title: 项目生效不是审批通过
page_key: project_status_vs_approval
belong: concepts
domain: tenant
status: draft
aliases: [项目已生效, 审批通过]
maps_to: tenant_project.project_status
field_targets: [tenant_project.project_status, tenant_project_approval.wf_status]
sources: ['code_path:TenantProjectDaoImpl.java:35', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/项目上线审批流程.md']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_project, tenant_project_approval]
also_confused_with: [online_approval_wf]
adjudication: boundary
---

# 项目生效不是审批通过

问「有效项目」过滤 project_status=1 且 enable=Y。
wf_status=FINISHED 是审批单通过，随后才可能生效项目。不要两列互代。

## 页面链接

- [[tables/tenant_project]]
- [[tables/tenant_project_approval]]
- [[dicts/tenant_project__project_status]]
- [[dicts/tenant_project_approval__wf_status]]
- [[processes/tenant_project__project_status]]
- [[processes/tenant_project_approval__wf_status]]
- [[concepts/online_approval_wf]]
