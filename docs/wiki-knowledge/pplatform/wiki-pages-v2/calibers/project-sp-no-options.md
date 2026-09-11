---
type: caliber
title: 立项审批编号下拉范围
page_key: caliber/project-sp-no-options
domain: 微企链立项与项目审批
status: draft
aliases:
  - 立项审批编号下拉
  - listProjectSpNo 口径
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalApplication.java#listProjectSpNo
contract_version: "0.1"
---

上线审批发起页的「立项审批编号」下拉只能看到两类记录：审批已通过（`act_procinst_status='2'`）且未被逻辑删除（`enable='Y'`）。排序键是 `sp_pass_time` 倒序，即最近通过的排在最前。

这条口径决定了上线审批可以引用哪些立项（见 [[concepts/sp-no-bridge]]），与导出范围的区别在于它额外收紧了 `enable`，见 [[calibers/wechat-approval-export-scope]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该口径的历史变更记录。

```ground:caliber
name: 立项审批编号下拉范围
predicate: "wechat_project_approval_apply.act_procinst_status = '2' AND wechat_project_approval_apply.enable = 'Y'"
scope: 上线审批发起页『立项审批编号』下拉
evidence: "code_path:ProjectApprovalApplication.java#listProjectSpNo"
```