---
type: concept
title: 上线审批授信不是额度审核
page_key: approval_credit_not_quota
belong: concepts
domain: remaining
status: draft
aliases: [额度审核工作流, 授信额度]
maps_to: tenant_project_approval_flow_credit.credited_cust_id
field_targets: [tenant_project_approval_flow_credit.credited_cust_id]
sources: ['document_claim:额度审核工作流.md#14', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_project_approval_flow_credit]
also_confused_with: [online_approval_wf]
adjudication: boundary
---

# 上线审批授信不是额度审核

document_claim:额度审核工作流.md#14 是客户端额度维护多级审批，pplatform-web 无对应业务表。
本库 tenant_project_approval_flow_credit 是项目上线审批授信（被授信方/授信方）。不要用这张表回答额度审核工作流。

## 页面链接

- [[tables/tenant_project_approval_flow_credit]]
- [[concepts/online_approval_wf]]
