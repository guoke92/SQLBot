---
type: process
title: 企业变更记录审核状态机 (cust_change_record.status)
page_key: cust_change_record_status
domain: 企业变更与运营变更
status: draft
aliases: [变更审核状态机, 变更流程状态, CUST_CHECK]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustCompanyInfoApplication.java
  - code:CustChangeApplication.java
  - db:cust_change_record
contract_version: "0.1"
belong: processes
---

本状态机描述单条变更记录（[[cust_change_record]]）从发起到终态的流转，状态值来自 `OperApiConstants.CheckStatus` 并以 `name()` 落库。它与 [[cust_company_info_cust_status]]（企业生命周期）不是同一状态轴：[[change_status]] 页面记录了三者的边界。

终态为 `CUST_CHECK_PASS` / `CUST_CHECK_REJECT`；非终态记录才允许被流程重建（[[change_rebuild]]、[[rebuildable_change_process]]）。DB 中还存在历史默认值 `'1'`，代码常量中无对应语义，见 REVIEW。

## 需求背景

变更由平台发起、运营中台审核，因此状态机需要表达「发起 → 审核中 → 通过/拒绝」的主干，以及两个非主干分支：中台退回让客户补充（`CUST_CHECK_BACKTOCUSTOM`）与客户重新发起时拒绝旧流程（`CUST_CHECK_REJECT`）。

## 版本演进

v0.1：首次抽取状态取值与四条迁移；`'1'` 历史默认值语义未声明，待与历史数据/旧版本对齐。

```ground:process
name: 企业变更记录审核状态机
field: cust_change_record.status
states:
  - value: CUST_CHECK_INIT
    label: 变更发起
    source: code_const
  - value: CUST_CHECK_CHECKING
    label: 审核中
    source: code_const
  - value: CUST_CHECK_BACKTOCUSTOM
    label: 退回客户补充
    source: code_const
  - value: CUST_CHECK_PASS
    label: 审核通过
    source: code_const
  - value: CUST_CHECK_REJECT
    label: 审核拒绝
    source: code_const
  - value: "1"
    label: 历史默认值（语义未声明）
    source: db_dist
transitions:
  - from: CUST_CHECK_INIT
    event: 发起变更同步运营中台
    to: CUST_CHECK_CHECKING
    evidence: "code_path:CustCompanyInfoApplication.java#submitCust(CheckStatus.CUST_CHECK_INIT) + OperApiConstants.CheckStatus"
  - from: CUST_CHECK_CHECKING
    event: 运营中台审核退回
    to: CUST_CHECK_BACKTOCUSTOM
    evidence: "code_path:CustCompanyInfoApplication.java#syncClientForSimple(CheckStatus.CUST_CHECK_BACKTOCUSTOM)"
  - from: CUST_CHECK_CHECKING
    event: 客户操作重新发起/拒绝旧流程
    to: CUST_CHECK_REJECT
    evidence: "code_path:CustChangeApplication.java#changeRebuild"
  - from: "*非终态"
    event: 流程重建
    to: CUST_CHECK_REJECT
    evidence: "code_path:CustChangeApplication.java#changeRebuild(notIn PASS,REJECT 取最新非终态记录后调用 operCustFacade.changeRejectProcess)"
```

相关页面：[[cust_change_record]]、[[change_status]]、[[change_rebuild]]、[[rebuildable_change_process]]、[[company_in_change]]。

---REVIEW: process | 企业变更记录审核状态机 (cust_change_record.status)---
状态取值 `'1'` 仅有 DB 分布证据，代码常量 `OperApiConstants.CheckStatus` 中不存在该值，且现有迁移均不产生该状态。需确认是历史版本遗留、初始化默认值，还是存在未覆盖的写入点；在确认前，任何按 `status` 过滤的口径都应显式排除或解释 `'1'`。
---END REVIEW---