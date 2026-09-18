---
type: concept
title: 审批关联项目编码
page_key: tenant_project_code_join
belong: concepts
domain: tenant
status: draft
aliases: [项目审批关联]
maps_to: tenant_project_approval.ref_tenant_project_approval_tenant_project
field_targets: [tenant_project_approval.ref_tenant_project_approval_tenant_project,
  tenant_project.code]
sources: ['code_path:ProjectApprovalApplication.java:253', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/项目上线审批流程.md']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_project_approval, tenant_project]
also_confused_with: [project_status_vs_approval, refer_copy_project]
adjudication: boundary
---

# 审批关联项目编码

L0 可能把审批接到项目 id。代码是项目 code = ref_tenant_project_approval_tenant_project。跨贴牌复制钉 refer_tenant_project_id，不是这条审批关联。

## 页面链接

- [[tables/tenant_project]]
- [[tables/tenant_project_approval]]
- [[concepts/project_status_vs_approval]]
- [[concepts/refer_copy_project]]
