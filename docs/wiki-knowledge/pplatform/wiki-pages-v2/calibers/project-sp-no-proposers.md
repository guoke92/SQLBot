---
type: caliber
title: 立项审批编号取关联人员
page_key: project-sp-no-proposers
domain: 微企链立项与项目审批
status: draft
aliases:
  - getProposerByApprovalNo 口径
  - 按 spNo 反查人员
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalApplication.java#getProposerByApprovalNo
contract_version: "0.1"
belong: calibers
---

当用户在发起页选定了立项审批编号后，系统按该编号反查这条立项上的方案经理、业务经理与运营人，用于带出审批参与人。取数条件是 `sp_no` 等值匹配且记录未逻辑删除。

这条口径保证了「一个 sp_no 只对应一条立项」，因为 `sp_no` 本身是唯一索引；人员字段的存储形态（姓名 CSV、企微 userId JSON 数组、运营人员 operation_id）各不相同，见 [[concepts/solution-manager-identity]]、[[concepts/operation-id-contact-reference]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该口径的历史变更记录。

```ground:caliber
name: 立项审批编号取关联人员
predicate: "wechat_project_approval_apply.sp_no = ? AND enable = 'Y'"
scope: 按 spNo 反查方案经理/业务经理/运营人
evidence: "code_path:ProjectApprovalApplication.java#getProposerByApprovalNo"
```