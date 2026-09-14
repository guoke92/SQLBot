---
type: process
title: 运营中台客户事件检查状态机
page_key: cust_event_check_status
domain: 平台事件监听与同步
status: draft
aliases:
  - 客户事件检查流程
  - 回调检查状态机
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:CustSyncEventProvider.java:onEvent
  - code:CustSyncEventProvider.java:processCustEvent
contract_version: "0.1"
belong: processes
---

描述 [[client_cust_event]] 的 `checkStatus` 在外部回调与平台处理之间的流转边界。关键点在于：审核通过与拒绝两个状态在本方法内不落库、不处理，交由工作流审核执行器。

## 需求背景

需求文档主张「用户邀请→激活→同步用户到 SSO、同步用户到 AMS 运营中台」，其事件入口即本流程的外部回调；但审核结论类事件（PASS/REJECT）必须由工作流执行器 `CustWorkflowAuditCommitProcessor` 处理，以避免与工作流双写，见 [[external_callback_skip_pass_reject]]。变更广播（`isChangeBroadcast=true`）时仍走本方法。

## 版本演进

- 平台侧发起的检查状态由 `operCustFacade.doSyncClient` 写入 `CUST_CHECK_INIT`，取值见 [[client_cust_event_check_status]]。
- 其余客户事件经 `processCustEvent → custSyncEventProcessor.doEvent` 按事件类型落库，是本流程与用户/企业同步（[[operator_sync_branch]]、[[company_status_sync]]）的分界。

```ground:process
name: 运营中台客户事件检查状态
field: ClientCustEvent.custEnterprise.checkStatus
states:
  - value: CUST_CHECK_INIT
    label: 提交/审核发起
    source: code_const
  - value: CUST_CHECK_PASS
    label: 审核通过
    source: code_const
  - value: CUST_CHECK_REJECT
    label: 审核拒绝
    source: code_const
  - value: CUST_CHECK_BACKTOCUSTOM
    label: 退回客户确认
    source: code_const
transitions:
  - from: CUST_CHECK_PASS
    event: 外部回调 onEvent(isChangeBroadcast=false)
    to: "(跳过/由工作流执行器处理)"
    evidence: "code_path:CustSyncEventProvider.java:onEvent"
  - from: CUST_CHECK_REJECT
    event: 外部回调 onEvent(isChangeBroadcast=false)
    to: "(跳过/由工作流执行器处理)"
    evidence: "code_path:CustSyncEventProvider.java:onEvent"
  - from: "(其它)"
    event: processCustEvent → custSyncEventProcessor.doEvent
    to: 按客户事件类型落库
    evidence: "code_path:CustSyncEventProvider.java:processCustEvent"
```