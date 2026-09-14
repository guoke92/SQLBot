---
type: rule
title: "审核轨迹取数规则"
page_key: audit_track_fetch
domain: "customer-onboarding"
status: draft
aliases:
  - "审批人取数规则"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustWorkflowAuditCommitProcessor.java:process"
contract_version: "0.1"
belong: rules
---

平台录入场景取审批历史第 1 条作为审批人，其他认证方式取最后 1 条，落库到企业主表的审批人与审批人名称字段。口径细节见 [[calibers/callback_audit_track_fetch]]，载体见 [[tables/cust_company_info]]。

## 需求背景

需求文档要求审核结果可追溯到操作人；不同发起方式下审批历史的方向不同，故需分支取数。

## 版本演进

- 该规则随拉取式执行器一并引入（见 [[rules/workflow_callback_routing]]）；被废弃的旧处理器不负责轨迹回填。

```ground:rule
name: "审核轨迹取数规则"
content: "平台录入(INVITE_AGW)取审批历史第 1 条作为审批人，其他认证方式取最后 1 条。"
impact: "决定 checkBy/checkByName 落库值"
field_targets:
  - "cust_company_info.check_by"
  - "check_by_name"
evidence: "code_path:CustWorkflowAuditCommitProcessor.java:process"
```

相关：[[calibers/callback_audit_track_fetch]]、[[tables/cust_company_info]]、[[processes/workflow_check_status_machine]]。