---
type: rule
title: 同一项目不能重复发起在途审批
page_key: no_duplicate_running_approval
belong: rules
domain: tenant
status: draft
field_targets: [tenant_project_approval.wf_status, tenant_project_approval.ref_tenant_project_approval_tenant_project]
sources: ['code_path:ProjectApprovalApplication.java:345']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_project_approval]
---

# 同一项目不能重复发起在途审批

同一项目 code 已有 PENDING 或 RUNNING 的上线审批则拒绝再发起。

```ground:rule
rule: 同一项目不能重复发起在途审批
field_targets: [tenant_project_approval.wf_status, tenant_project_approval.ref_tenant_project_approval_tenant_project]
impact: write_constraint
content: 同一项目 code 已有 PENDING 或 RUNNING 的上线审批则拒绝再发起。
evidence: code_path:ProjectApprovalApplication.java:345
```

## 页面链接

- [[tables/tenant_project_approval]]
- [[dicts/tenant_project_approval__wf_status]]
- [[processes/tenant_project_approval__wf_status]]
