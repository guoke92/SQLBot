---
type: rule
title: 运营中台审核回调分工
page_key: audit-callback-dispatch
domain: 企业变更与运营变更
status: draft
aliases: [CustSyncEventProvider, isChangeBroadcast]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustSyncEventProvider.java:onEvent
contract_version: "0.1"
belong: rules
---

`CUST_CHECK_PASS` / `CUST_CHECK_REJECT` 回调由工作流审核执行器 `CustWorkflowAuditCommitProcessor` 处理，`CustSyncEventProvider.onEvent` 直接跳过（`isChangeBroadcast=true` 的变更广播除外）。这解释了 [[processes.cust-change-record-status]] 中两个终态迁移的 evidence 为何指向「跳过」而非写入。

## 需求背景

审批终态需要携带工作流上下文，只有执行器具备处理条件；事件提供者若重复处理会导致状态被写两次或覆盖，因此显式跳过，同时为变更广播保留独立通道。字段影响面见 [[concepts.change-status]]（变更单状态与企业准入状态分属两条线）。

## 版本演进

v0.1：首次登记，规则来自 `CustSyncEventProvider.onEvent`。

```ground:rule
name: 运营中台审核回调分工
content: CUST_CHECK_PASS / CUST_CHECK_REJECT 回调由工作流审核执行器 CustWorkflowAuditCommitProcessor 处理，CustSyncEventProvider.onEvent 直接跳过（isChangeBroadcast=true 的变更广播除外）
impact: 避免审批终态被重复处理，变更广播走独立通道
field_targets:
  - cust_change_record.status
  - cust_company_info.check_status
evidence: code_path:CustSyncEventProvider.java:onEvent
```