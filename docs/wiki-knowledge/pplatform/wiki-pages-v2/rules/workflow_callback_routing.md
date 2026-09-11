---
type: rule
title: "工作流回调路由规则"
page_key: "rules/workflow_callback_routing"
domain: "customer-onboarding"
status: draft
aliases:
  - "通过拒绝走拉取处理器"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustSyncEventProvider.java:onEvent"
  - "code_path:CustWorkflowAuditCommitProcessor.java:process"
contract_version: "0.1"
---

运营中台建档审核回调进入本域后被拆成两路：终态事件被同步事件提供者跳过，改由工作流审核执行器主动拉取中台数据后处理；中间状态（审核中、退回）仍由事件提供者落库。这条规则决定了「通过/拒绝」的唯一落库入口，避免重复处理。相关状态机见 [[processes/workflow_check_status_machine]]。

## 需求背景

中台回调仅携带状态描述，终态所需的审批轨迹等数据需二次拉取；因此把终态从事件通道中摘出，交由拉取式执行器完成，是保证数据完整的工程约束。

## 版本演进

- 路由方式从「事件通道全量处理」演进为「终态拉取 + 中间态事件」的双通道；排查状态未更新问题时需先确认事件属于哪一通道。

```ground:rule
name: "工作流回调路由规则"
content: "运营中台建档审核回调中，checkStatus 为 CUST_CHECK_PASS 或 CUST_CHECK_REJECT 的事件被 CustSyncEventProvider.onEvent 直接跳过，改由 CustWorkflowAuditCommitProcessor 拉取中台数据后处理；CustSyncEventProvider 只落审核中/退回等中间状态。"
impact: "决定通过/拒绝的落库入口，避免重复处理"
field_targets:
  - "cust_company_info.check_status"
  - "cust_build_status"
evidence: "code_path:CustSyncEventProvider.java:onEvent;CustWorkflowAuditCommitProcessor.java:process"
```

相关：[[processes/workflow_check_status_machine]]、[[tables/cust_company_info]]、[[rules/workflow_processor_scope_comment_mismatch]]。