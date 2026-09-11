---
type: rule
title: 拒绝/通过回调由工作流处理
page_key: rules/reject-pass-callback-workflow
domain: 平台事件监听与同步
status: draft
aliases:
  - onEvent 审核状态短路
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustSyncEventProvider.java:onEvent
contract_version: "0.1"
---

回调路由去重规则：`onEvent` 非变更广播时，checkStatus 为 CUST_CHECK_PASS 或 CUST_CHECK_REJECT 的记录直接跳过，仅处理审核中，避免与 CustWorkflowAuditCommitProcessor 重复处理。

## 需求背景
运营中台的审核终态既会通过事件回调到达产融，也会由工作流提交处理器处理；若两条路径都消费终态，会造成 [[tables/cust_company_info]] 建档状态的重复推进。因此回调侧只处理「审核中」这一中间态，终态交由工作流处理。

## 版本演进
- v0 契约：短路条件取自 `CustSyncEventProvider.onEvent`；与 [[processes/cust-company-build-status]] 中 CUST_BUILDING → BUILD_SUCCESS / CUST_CONFIRM_AWAIT 的迁移路径互补。

```ground:rule
name: 拒绝/通过回调由工作流处理
content: "onEvent 非变更广播时，checkStatus 为 CUST_CHECK_PASS 或 CUST_CHECK_REJECT 的记录直接跳过，仅处理审核中，避免与 CustWorkflowAuditCommitProcessor 重复处理"
impact: 回调路由去重，防止重复消费
field_targets:
  - cust_company_info.cust_build_status
evidence: "CustSyncEventProvider.java:onEvent"
related_pages:
  - tables/cust_company_info
  - processes/cust-company-build-status
```