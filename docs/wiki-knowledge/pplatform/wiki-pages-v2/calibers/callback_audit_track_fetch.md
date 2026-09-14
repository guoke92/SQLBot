---
type: caliber
title: "回调审核轨迹取数"
page_key: callback_audit_track_fetch
domain: "customer-onboarding"
status: draft
aliases:
  - "审批人取数口径"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustWorkflowAuditCommitProcessor.java:process"
contract_version: "0.1"
belong: calibers
---

回填审核轨迹（审批人与审批人名称）时，取数位置随建档方式而变：平台录入取审批历史第 1 条，其他方式取最后 1 条。落库字段见 [[tables/cust_company_info]]，规则条目见 [[rules/audit_track_fetch]]。

## 需求背景

需求文档要求审核结论可溯源到操作人；由于平台录入由平台侧发起、审批历史顺序与客户自主认证相反，取数位置需要分支处理。

## 版本演进

- 分支条件绑定 `identify_style`，新增建档方式时若未归类，会默认落入「取最后 1 条」分支，需同步维护。

```ground:caliber
name: "回调审核轨迹取数"
predicate: "identify_style = 'INVITE_AGW' 取 custWkflAppHistoryList 第 1 条；否则取最后 1 条"
scope: "CustWorkflowAuditCommitProcessor 填充 checkBy/checkByName"
evidence: "code_path:CustWorkflowAuditCommitProcessor.java:process"
```

相关：[[tables/cust_company_info]]、[[rules/audit_track_fetch]]、[[processes/workflow_check_status_machine]]。