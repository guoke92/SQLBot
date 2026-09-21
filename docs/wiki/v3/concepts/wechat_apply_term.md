---
type: concept
title: 企微立项审批单
page_key: wechat_apply_term
belong: concepts
domain: remaining
status: draft
aliases: [企微审批, 立项申请, 企微立项审批]
maps_to: wechat_project_approval_apply.sp_no
field_targets: [wechat_project_approval_apply.sp_no]
sources: ['code_path:WechatProjectApprovalApplication.java:148', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [wechat_project_approval_apply]
also_confused_with: [online_approval_wf, simulated_project_apply, wechat_prd_term,
  async_batch_term]
adjudication: boundary
---

# 企微立项审批单

document_claim:企微立项审批集成.md#13：企微同步/导入的立项申请在 wechat_project_approval_apply。
document_claim:项目立项统计与上线审批产品映射.md#19：按产品名称过滤立项编号，仍是本表，不是 tenant_project_approval。
项目上线审批在 tenant_project_approval，不要互代。立项统计与企微立项共用本表。

## 页面链接

- [[tables/wechat_project_approval_apply]]
- [[concepts/async_batch_term]]
- [[concepts/online_approval_wf]]
- [[concepts/simulated_project_apply]]
- [[concepts/wechat_prd_term]]
