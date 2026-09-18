---
type: rule
title: 再发起审批先失效已生效项目
page_key: resubmit_invalidates_effective_project
belong: rules
domain: tenant
status: draft
field_targets: [tenant_project.project_status]
sources: ['code_path:ProjectApprovalApplication.java:650']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_project]
---

# 再发起审批先失效已生效项目

非新增项目正式发起上线审批时，project_status 已是 1 或 2 则先 invalid 写成 2。
待生效 0 跳过。不改审批 wf_status。


```ground:rule
rule: 再发起审批先失效已生效项目
field_targets: [tenant_project.project_status]
impact: write_constraint
content: '非新增项目正式发起上线审批时，project_status 已是 1 或 2 则先 invalid 写成 2。

  待生效 0 跳过。不改审批 wf_status。

  '
evidence: code_path:ProjectApprovalApplication.java:650
```

## 页面链接

- [[tables/tenant_project]]
- [[dicts/tenant_project__project_status]]
- [[processes/tenant_project__project_status]]
