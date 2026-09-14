---
type: concept
title: 打款交易标识（trans_id 与 trace_no）
page_key: trans-id-vs-trace-no
domain: 企业银行账户
status: draft
aliases: [trans_id, trace_no, OriginalTxSN]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustAccountApplication.java
contract_version: "0.1"
maps_to: trans_id=我方发起打款后写入的银行 OriginalTxSN；trace_no=银行返回的系统跟踪号
field_targets:
  - cust_account_info.trans_id
  - cust_account_info.trace_no
adjudication: boundary
also_confused_with:
  - 两者互相混用
boundary: 查询打款结果与打款验证都以 trans_id（OriginalTxSN）为入参；trace_no 仅落库留痕，不参与后续调用。
belong: concepts
---

打款链路中存在两个容易混淆的标识：`trans_id` 是我方发起打款后写入的银行 OriginalTxSN，`trace_no` 是银行返回的系统跟踪号。两者均落库于 [[tables/cust_account_info]]，流程语境见 [[processes/account-cnaps-payment-auth-state]]。

## 需求背景

查询打款结果与打款验证都需要一个与银行侧一致的请求标识，现行实现统一以 trans_id 为入参，并在申请阶段就把它写入账户记录；trace_no 仅用于留痕排查，不参与后续调用。验证前置约束见 [[rules/payment-confirm-precondition]]。

## 版本演进

v0 契约按现状固化：两标识职责分离，混用会导致银行侧查不到记录。

## 判定边界

查询打款结果与打款验证都以 trans_id（OriginalTxSN）为入参；trace_no 仅落库留痕，不参与后续调用。