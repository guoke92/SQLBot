---
type: rule
title: 同一项目不能重复发起在途审批
page_key: no_duplicate_running_approval
belong: rules
domain: tenant
status: draft
field_targets: [tenant_project_approval.wf_status, tenant_project_approval.ref_tenant_project_approval_tenant_project]
sources: ['code_path:ProjectApprovalApplication.java:287']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_project_approval]
---

# 同一项目不能重复发起在途审批

现网 assertNoApproval：同一项目 code 已有 PENDING 或 RUNNING 则拒绝再发起（prepareWizardApproval）。
document_claim:V1.37 设计拟放开多在途——以现网代码为准，未落地前不要按多在途口径回答。


```ground:rule
rule: 同一项目不能重复发起在途审批
field_targets: [tenant_project_approval.wf_status, tenant_project_approval.ref_tenant_project_approval_tenant_project]
impact: write_constraint
content: '现网 assertNoApproval：同一项目 code 已有 PENDING 或 RUNNING 则拒绝再发起（prepareWizardApproval）。

  document_claim:V1.37 设计拟放开多在途——以现网代码为准，未落地前不要按多在途口径回答。

  '
evidence: code_path:ProjectApprovalApplication.java:287
```

## 页面链接

- [[tables/tenant_project_approval]]
- [[dicts/tenant_project_approval__wf_status]]
- [[processes/tenant_project_approval__wf_status]]
