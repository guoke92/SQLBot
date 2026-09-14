---
type: caliber
title: 银行账户（账户类型）
page_key: bank_account_type
domain: 企业银行账户
status: draft
aliases:
  - account_type=BANK
  - 银行账户口径
oid: 1
scope:
  databases:
    - customer_management
sources:
  - db
contract_version: "0.1"
belong: calibers
---

# 银行账户（账户类型）

口径判断：`cust_account_info.account_type = '1'`，是账户类型的主口径。

## 需求背景

账户类型统计与筛选需要区分银行账户与运营费账户、收款账户，取值审计见 [[account_type]]。

## 版本演进

- `BANK` 占 48428/48468，为主口径；`OPERATION_FEE_ACCOUNT`(30)、`received`(1)、`'1'`(5) 为少数取值，按 `BANK` 过滤时会漏掉这些账户。

```ground:caliber
name: 银行账户（账户类型）
predicate: cust_account_info.account_type = '1'
scope: 占 48428/48468，是账户类型主口径
evidence: db
```