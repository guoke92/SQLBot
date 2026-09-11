---
type: rule
title: 正式首次提交回写 wechat_audit_no
page_key: rule/approval-no-writeback-on-submit
domain: 微企链立项与项目审批
status: draft
aliases:
  - 立项编号回写租户项目
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalApplication.java
  - db:tenant_project_approval
contract_version: "0.1"
---

上线审批单据上填写的 `sp_no` 会在「正式首次提交」时被回写到 `tenant_project.wechat_audit_no`，把项目与企微立项审批正式绑定。触发条件是首次提交且非草稿，草稿保存不会产生回写。

这里的「首次」由 `ref_tenant_project_approval_tenant_project_approval` 是否为空界定：为空表示首次发起（见 [[tables/tenant_project_approval]]）。桥接键的全局含义见 [[concepts/sp-no-bridge]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 正式首次提交回写 wechat_audit_no
subject: tenant_project_approval.sp_no
evidence: code
source_meaning: 关联的企微立项审批编号，正式首次提交时回写 tenant_project.wechat_audit_no
```