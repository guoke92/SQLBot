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
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_project_approval]
also_confused_with: [project_status_vs_approval, wechat_apply_term, approval_whitelist,
  approval_credit_not_quota]
adjudication: boundary
---

# 项目上线审批

需求「项目上线审批流程」落在 tenant_project_approval。
wf_status：PENDING/RUNNING/FINISHED/TERMINATED/REVOKED（displayName=审批撤销，V1.35+）。
REVOKED 是发起人撤销（revokeApproval），不是 TERMINATED（审批拒绝）；撤销不改项目 project_status。
按项目 code 关联，不是项目 id。企微立项单是另一张表。
document_claim:项目上线审批催办.md#31：催办仅 RUNNING、5 分钟一次发企微；ProjectApprovalRemindApplication 不写本表。
document_claim:项目上线审批跨节点退回.md#15：退回写节点，wf_status 仍等流程结束监听。
现网 assertNoApproval：同一项目仍禁止重复 PENDING/RUNNING；列表「最新一条」用 is_latest=Y。
document_claim:V1.37 设计拟放开多在途并增加 project_config_deleted/project_name_snapshot 留底列——live 库与现网代码尚未落地，勿当 confirmed 列。

## 页面链接

- [[tables/tenant_project_approval]]
- [[dicts/tenant_project_approval__wf_status]]
- [[processes/tenant_project_approval__wf_status]]
- [[concepts/approval_credit_not_quota]]
- [[concepts/approval_whitelist]]
- [[concepts/project_status_vs_approval]]
- [[concepts/wechat_apply_term]]
