---
type: rule
title: "新增项目首次正式提交回写立项编号"
page_key: "rule/first_formal_submit_backfill_wechat_audit_no"
domain: "tenant-project"
status: published
aliases: ["回写立项编号"]
oid: 1
sources:
  - "semantic_analysis"
contract_version: "0.1"
field_targets: [tenant_project.wechat_audit_no, tenant_project_approval.sp_no]
scope:
  databases: [lowcode_pplatform]
---

上线审批 isAdd=Y 且首次发起时，将审批 sp_no 回写 tenant_project.wechat_audit_no 并推送 EFFECTED 事件。

## 需求背景
规则来源于 ProjectApprovalApplication.backfillProjectSpNoOnSubmit 方法（证据字符串在语义分析中被截断，完整路径需补充确认）。

## 版本演进
v0.1 版本基于部分代码路径证据建立，证据截断处需后续完善。

```ground:rule
name: "新增项目首次正式提交回写立项编号"
content: "上线审批 isAdd=Y 且首次发起时，将审批 sp_no 回写 tenant_project.wechat_audit_no 并推送 EFFECTED 事件"
impact: "tenant_project.wechat_audit_no 更新"
field_targets:
  - "tenant_project.wechat_audit_no"
  - "tenant_project_approval.sp_no"
evidence: "code_path:ProjectApprovalApplication.java:backfillProjectSpNoOnSub"
```

相关：[[tenant_project]] [[tenant_project_approval]] [[project_approval_no_wechat]]