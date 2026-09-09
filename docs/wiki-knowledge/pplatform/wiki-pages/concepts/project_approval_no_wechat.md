---
type: concept
title: "立项审批编号"
page_key: project_approval_no_wechat
belong: concepts
domain: "tenant-project"
status: published
aliases: ["企微审批编号", "wechat_audit_no", "立项编号"]
oid: 1
sources:
  - "semantic_analysis"
contract_version: "0.1"
maps_to: "tenant_project.wechat_audit_no / tenant_project_approval.sp_no"
field_targets: ["tenant_project.wechat_audit_no", "tenant_project_approval.sp_no"]
adjudication: "boundary"
also_confused_with: ["approval_no"]
scope:
  databases: [lowcode_pplatform]
---

“立项审批编号”指企微立项审批编号，正式提交时从审批表 sp_no 回写到租户项目表的 wechat_audit_no 字段。与审批编号 approval_no 不同。

## 需求背景
术语桥接识别立项编号与审批编号的边界：sp_no 为源，wechat_audit_no 为回写字段。

## 版本演进
v0.1 版本完成边界判定，后续需确认回写时机。

相关：[[tenant_project]] [[tenant_project_approval]] [[first_formal_submit_backfill_wechat_audit_no]]