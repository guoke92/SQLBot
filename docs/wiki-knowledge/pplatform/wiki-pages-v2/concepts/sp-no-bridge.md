---
type: concept
title: sp_no 立项—上线审批桥接键
page_key: concept/sp-no-bridge
domain: 微企链立项与项目审批
status: draft
aliases:
  - 企微审批编号
  - wechat_audit_no
  - 立项编号回写
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - db:wechat_project_approval_apply
  - code_path:ProjectApprovalApplication.java
  - code_path:WechatProjectApprovalApplication.java#exportWechatApprovalInfo
contract_version: "0.1"
maps_to:
  - wechat_project_approval_apply.sp_no
  - tenant_project_approval.sp_no
  - tenant_project.wechat_audit_no
field_targets:
  - table: wechat_project_approval_apply
    field: sp_no
  - table: tenant_project_approval
    field: sp_no
adjudication: sp_no 是企微立项审批的业务编号，在立项申请表上是唯一索引；上线审批表以它引用立项，并在正式首次提交时把它回写到 tenant_project.wechat_audit_no。同一编号在三处出现，指向的是同一次企微立项审批。
also_confused_with:
  - tenant_project_approval.approval_no（上线审批业务编号，平台业务编号服务生成，与 sp_no 不同源）
  - tenant_project_approval.related_approval_no（关联审批编号）
sources: ["enrich:wiki-admin"]
---

`sp_no` 把「企微侧」与「平台侧」串起来：企微同步以它为匹配键做只更新不新增的 upsert（见 [[rules/wechat-import-match-by-sp-no]]），平台发起上线审批时以它引用立项并回写租户项目（见 [[rules/approval-no-writeback-on-submit]]），可用编号范围由 [[calibers/project-sp-no-options]] 决定。

它与 `approval_no` 的区别必须分清：后者是上线审批自己的业务编号，由平台业务编号服务生成，与企微无关。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该概念的历史变更记录。

相关页面：[[tables/wechat_project_approval_apply]]、[[tables/tenant_project_approval]]。

相关：[[wechat_project_approval_apply]]
