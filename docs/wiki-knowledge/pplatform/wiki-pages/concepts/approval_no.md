---
type: concept
title: "审批编号"
page_key: "concept/approval_no"
domain: "tenant-project"
status: published
aliases: ["approvalNo", "project_approval_no", "审批编号"]
oid: 1
sources:
  - "semantic_analysis"
contract_version: "0.1"
maps_to: "tenant_project_approval.approval_no"
field_targets: ["tenant_project_approval.approval_no"]
adjudication: "boundary"
also_confused_with: ["wechat_audit_no", "sp_no"]
scope:
  databases: [lowcode_pplatform]
---

“审批编号”指上线审批自身编号，存储在 tenant_project_approval.approval_no，区别于立项审批编号 sp_no/wechat_audit_no。

## 需求背景
术语桥接识别审批编号与立项审批编号的混淆风险，需要明确边界。

## 版本演进
v0.1 版本完成边界判定，后续需补充 approval_no 的生成逻辑证据。

相关：[[tenant_project_approval]] [[project_approval_no_wechat]]