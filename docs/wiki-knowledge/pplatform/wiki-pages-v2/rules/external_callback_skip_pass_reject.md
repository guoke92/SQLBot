---
type: rule
title: 外部回调不处理审核通过与拒绝
page_key: external_callback_skip_pass_reject
domain: 平台事件监听与同步
status: draft
aliases:
  - onEvent 跳过规则
  - PASS/REJECT 不由回调处理
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:CustSyncEventProvider.java:onEvent
contract_version: "0.1"
belong: rules
---

外部回调 `onEvent(isChangeBroadcast=false)` 遇到 `CUST_CHECK_PASS` 或 `CUST_CHECK_REJECT` 时直接返回，不做任何处理。

## 需求背景

审核结论类事件必须由工作流审核执行器 `CustWorkflowAuditCommitProcessor` 处理，回调侧再处理一次会造成与企业建档状态机（[[cust_build_status]]）的双写。变更广播（`isChangeBroadcast=true`）时仍走本方法。状态取值见 [[client_cust_event_check_status]]，整体流转见 [[cust_event_check_status]]。

## 版本演进

- 该跳过逻辑与「按事件类型落库」的 `processCustEvent` 分支并存，理解入口时需先看 `isChangeBroadcast` 与 `checkStatus` 两个判别条件。

```ground:rule
name: 外部回调不处理 PASS/REJECT
content: onEvent(isChangeBroadcast=false) 时若 checkStatus 为 CUST_CHECK_PASS 或 CUST_CHECK_REJECT，直接 return，交由工作流审核执行器 CustWorkflowAuditCommitProcessor 处理
impact: 避免与工作流审核双写；变更广播 isChangeBroadcast=true 时仍走本方法
field_targets: []
evidence: "code:CustSyncEventProvider.java:onEvent"
```