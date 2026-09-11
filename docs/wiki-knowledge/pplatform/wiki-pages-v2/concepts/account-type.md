---
type: concept
title: 账户类型（account_type）
page_key: concepts/account-type
domain: 企业银行账户
status: draft
aliases: [account_type, BANK, OPERATION_FEE_ACCOUNT]
oid: 1
scope:
  databases: [unknown]
sources:
  - db
contract_version: "0.1"
maps_to: 账户类型值（代码枚举基线缺失，取自 DB 实测）
field_targets:
  - cust_account_info.account_type
adjudication: boundary
also_confused_with:
  - "'1'、'received' 等脏值"
boundary: DB 默认值 BANK；OPERATION_FEE_ACCOUNT 为代码中未声明的真实类型，另存在 '1'/'received' 低量异常值，统计口径需排除或归并。
---

账户类型用于区分账户用途，落库字段为 `cust_account_info.account_type`（见 [[tables/cust_account_info]]），DB 默认值为 BANK。

## 需求背景

账户表同时承载还款账户与运营费账户等不同用途，按类型分流的统计与筛选需要一个稳定的取值集合；但代码枚举基线未声明 OPERATION_FEE_ACCOUNT，且存在 '1' / 'received' 等低量异常值，直接按枚举过滤会漏数。

## 版本演进

v0 契约按现状固化，取值集来自 DB 实测而非代码枚举；后续版本建议将 OPERATION_FEE_ACCOUNT 补入枚举并清理异常值。

## 判定边界

DB 默认值 BANK；OPERATION_FEE_ACCOUNT 为代码中未声明的真实类型，另存在 '1'/'received' 低量异常值，统计口径需排除或归并。