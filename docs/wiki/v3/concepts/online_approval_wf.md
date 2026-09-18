---
type: concept
title: 项目上线审批
page_key: online_approval_wf
belong: concepts
domain: tenant
status: draft
aliases: [上线审批, 立项审批, 催办, 审批催办, 审批撤回, 跨节点退回]
maps_to: tenant_project_approval.wf_status
field_targets: [tenant_project_approval.wf_status]
sources: ['code_path:ProjectApprovalWorkflowStatusEnum.java:16', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/项目上线审批流程.md']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_project_approval]
also_confused_with: [project_status_vs_approval, wechat_apply_term, approval_whitelist,
  approval_credit_not_quota]
adjudication: boundary
---

# 项目上线审批

需求「项目上线审批流程」落在 tenant_project_approval。PENDING 待发起，RUNNING 审批中，FINISHED 通过，TERMINATED 拒绝。
按项目 code 关联，不是项目 id。企微立项单是另一张表。
document_claim:项目上线审批催办.md#31：催办仅 RUNNING、5 分钟一次发企微；ProjectApprovalRemindApplication 不写本表。
document_claim:项目上线审批撤回.md#21 要「审批撤销」；现网枚举无 REVOKED，TERMINATED 注释是审批拒绝，不要把撤销当成拒绝。
document_claim:项目上线审批跨节点退回.md#15：退回写节点，wf_status 仍等流程结束监听。

## 页面链接

- [[tables/tenant_project_approval]]
- [[dicts/tenant_project_approval__wf_status]]
- [[processes/tenant_project_approval__wf_status]]
- [[concepts/approval_credit_not_quota]]
- [[concepts/approval_whitelist]]
- [[concepts/project_status_vs_approval]]
- [[concepts/wechat_apply_term]]
