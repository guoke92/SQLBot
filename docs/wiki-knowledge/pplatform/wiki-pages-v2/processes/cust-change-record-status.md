---
type: process
title: 客户变更单状态机（cust_change_record.status）
page_key: process.cust-change-record-status
domain: 企业变更与运营变更
status: draft
aliases: [变更单状态, 变更审批状态, CheckStatus]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_change_record
  - code_path:CustSyncEventProvider.java:onEvent
  - code_path:CustChangeApplication.java:changeRebuild
contract_version: "0.1"
---

变更单状态挂在 [[tables.cust_change_record]] 的 `status` 上，取值来自 `OperApiConstants.CheckStatus` 枚举：审核中（`CUST_CHECK_CHECKING`）、审核通过（`CUST_CHECK_PASS`，终态）、审核拒绝（`CUST_CHECK_REJECT`，终态）、退回客户（`CUST_CHECK_BACKTOCUSTOM`）。终态口径被流程重建直接使用，见 [[calibers.change-record-terminal-status]] 与 [[rules.change-record-terminal-filter]]。调用方重新发起变更时，会先结束旧流程并把旧单置为拒绝，见 [[rules.change-rebuild]]。

## 需求背景

审核终态由运营中台回调驱动：`CUST_CHECK_PASS` 与 `CUST_CHECK_REJECT` 回调统一交由工作流审核执行器处理，事件提供者 `CustSyncEventProvider.onEvent` 直接跳过，见 [[rules.audit-callback-dispatch]]。因此本状态机的终态写入并不在本模块内完成，本页只登记状态与可观测的流转。

## 版本演进

v0.1：首次登记。状态取值中 `1`（表默认值）、`CUSTS003`、`returnCust-<时间戳>` 为库表实测值，代码层未见对应枚举声明，暂按历史/脏值处理。

```ground:process
name: 客户变更单状态
field: cust_change_record.status
states:
  - value: "1"
    label: 待提交/初始（表默认值，代码层未见枚举声明）
    source: db_dist
  - value: CUST_CHECK_CHECKING
    label: 审核中
    source: code_enum
  - value: CUST_CHECK_BACKTOCUSTOM
    label: 退回客户
    source: db_dist
  - value: CUST_CHECK_PASS
    label: 审核通过（终态）
    source: code_enum
  - value: CUST_CHECK_REJECT
    label: 审核拒绝（终态）
    source: code_enum
  - value: CUSTS003
    label: 未识别的历史值（1 条）
    source: db_dist
  - value: "returnCust-<时间戳>"
    label: 历史退回标记，非标准枚举（13 条）
    source: db_dist
transitions:
  - from: CUST_CHECK_CHECKING
    event: 运营中台审核通过回调
    to: CUST_CHECK_PASS
    evidence: "code_path:CustSyncEventProvider.java:onEvent（CUST_CHECK_PASS 由 CustWorkflowAuditCommitProcessor 处理，onEvent 直接跳过）"
  - from: CUST_CHECK_CHECKING
    event: 运营中台审核拒绝回调
    to: CUST_CHECK_REJECT
    evidence: "code_path:CustSyncEventProvider.java:onEvent（CUST_CHECK_REJECT 同上，交由工作流审核执行器）"
  - from: CUST_CHECK_CHECKING
    event: 客户操作重新发起/流程重建（拒绝旧流程，发起新流程）
    to: CUST_CHECK_REJECT
    evidence: "code_path:CustChangeApplication.java:changeRebuild（取最新非终态记录，调 operCustFacade.changeRejectProcess 结束旧流程）"
```