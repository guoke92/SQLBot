---
type: table
title: client_cust_event 客户端客户事件表
page_key: client_cust_event
domain: 平台事件监听与同步
status: draft
aliases:
  - 客户事件
  - 运营中台客户事件
oid: 1
scope:
  databases: [lowcode_pplatform]
sources:
  - db:client_cust_event
  - code:CustSyncEventProvider.java:onEvent
contract_version: "0.1"
belong: tables
---

承载运营中台推送给平台的客户事件，`checkStatus` 记录当前审核检查状态，状态机见 [[cust_event_check_status]]。

## 需求背景

外部回调进入 `CustSyncEventProvider.onEvent`：当 `isChangeBroadcast=false` 且 `checkStatus` 为通过/拒绝时，本方法直接返回，交由工作流审核执行器处理，避免双写，见 [[external_callback_skip_pass_reject]]。其余事件经 `processCustEvent → custSyncEventProcessor.doEvent` 按客户事件类型落库。

## 版本演进

- 状态值以 `OperApiConstants.CheckStatus.name()` 落库（`CUST_CHECK_INIT` / `CUST_CHECK_PASS` / `CUST_CHECK_REJECT` / `CUST_CHECK_BACKTOCUSTOM`），与 `cust_info_sync.process_type` 用 `getCode()` 的写法不同，跨表比对需注意。

