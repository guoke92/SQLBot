---
type: concept
title: 企微审批单号
page_key: wechat_sp_no
domain: 微企链立项与项目审批
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: concepts
field_targets:
  - wechat_project_approval_apply.sp_no
  - tenant_project.wechat_audit_no
maps_to: wechat_project_approval_apply.sp_no
adjudication: synonym
also_confused_with: [tenant_project_approval.approval_no]
---

立项 `sp_no` 与项目 `wechat_audit_no`、上线单 `sp_no` 对齐同一企微单号。上线单自己的 `approval_no` 是平台审批编号。
