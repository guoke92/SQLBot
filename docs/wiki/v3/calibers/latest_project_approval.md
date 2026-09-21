---
type: caliber
title: 项目最新上线审批
page_key: latest_project_approval
belong: calibers
domain: tenant
status: draft
field_targets: [tenant_project_approval.is_latest, tenant_project_approval.enable,
  tenant_project_approval.ref_tenant_project_approval_tenant_project]
sources: ['code_path:ProjectApprovalApplication.java:253']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_project_approval, tenant_project]
---

# 项目最新上线审批

回答「该项目当前/最新审批单」。按项目 code 不是 id。历史审批 is_latest 不是 Y。
现网向导仍 assertNoApproval 禁止重复在途；查「全部在途」用 wf_status IN (PENDING,RUNNING)，不要只用 is_latest。
留底列 project_config_deleted 见 document_claim，列未上线前不写 predicate。


```ground:caliber
caliber: 项目最新上线审批
field_targets: [tenant_project_approval.is_latest, tenant_project_approval.enable,
  tenant_project_approval.ref_tenant_project_approval_tenant_project]
predicate: tenant_project_approval.is_latest = 'Y' AND tenant_project_approval.enable
  = 'Y' AND tenant_project_approval.ref_tenant_project_approval_tenant_project = :project_code
scope: global
boundary: '回答「该项目当前/最新审批单」。按项目 code 不是 id。历史审批 is_latest 不是 Y。

  现网向导仍 assertNoApproval 禁止重复在途；查「全部在途」用 wf_status IN (PENDING,RUNNING)，不要只用 is_latest。

  留底列 project_config_deleted 见 document_claim，列未上线前不写 predicate。

  '
using_relations:
- left: tenant_project.code
  right: tenant_project_approval.ref_tenant_project_approval_tenant_project
evidence: code_path:ProjectApprovalApplication.java:253
```

## 页面链接

- [[tables/tenant_project]]
- [[tables/tenant_project_approval]]
- [[dicts/tenant_project_approval__enable]]
- [[dicts/tenant_project_approval__is_latest]]
