---
type: caliber
title: 未发起打款认证
page_key: not_applied_payment_auth
domain: 企业银行账户
status: draft
aliases:
  - auth_state=APPLY_00
  - 未认证账户口径
oid: 1
scope:
  databases:
    - customer_management
sources:
  - db
contract_version: "0.1"
belong: calibers
---

# 未发起打款认证

口径判断：`cust_account_info.auth_state = 'APPLY_00'`，即尚未发起打款认证的账户。

## 需求背景

用于识别待认证账户存量，是[[payment_auth]]流程的起始集合，状态迁移见 [[bank_account_auth_state]]。

## 版本演进

- 该值为 DB 列默认值，占 49144 条，是存量账户的绝对主状态。

```ground:caliber
name: 未发起打款认证
predicate: cust_account_info.auth_state = 'APPLY_00'
scope: DB 列默认值，占 49144 条
evidence: db
```