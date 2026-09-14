---
type: concept
title: 默认账户
page_key: default_account
domain: 企业银行账户
status: draft
aliases:
  - 默认还款账号
  - 默认还款账户
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
maps_to: cust_account_info.default_account_flag
field_targets:
  - cust_account_info.default_account_flag
also_confused_with:
  - cust_account_info.account_type
adjudication: boundary
belong: concepts
field_targets: [cust_account_info.default_account_flag]
sources: ["enrich:wiki-admin"]
---

# 默认账户

业务上指企业用于默认还款的那一个银行账户，落库为 `cust_account_info.default_account_flag = '1'`，口径见 [[default_repayment_account]]。

## 需求背景

企业可维护多个账户，但还款类业务只认“默认”那一个，因此需要唯一的默认标记与置默认操作（[[single_default_account]]）。

## 版本演进

- 默认标记由写时互斥维护（`setDefaultFlag`/`afterSave`），不是查询时按时间或类型推导。

## 边界（adjudication: boundary）

`default_account_flag` 是企业维度内的默认标记，由 `setDefaultFlag`/`afterSave` 互斥维护；`account_type` 描述账户性质（银行/运营费账户），二者不可互推。统计“默认账户数”必须用 `default_account_flag`，不能用 `account_type`。

相关：[[cust_account_info]]
