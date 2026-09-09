---
type: caliber
title: 普通银行账户
page_key: normal-bank-account
belong: calibers
domain: 企业银行账户与第三方银行
status: published
aliases: ["BANK", "普通账户"]
oid: 1
sources: ["db"]
contract_version: "0.1"
field_targets: [cust_account_info.account_type]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

口径“普通银行账户”用于识别企业录入的一般银行结算账户。其判定条件为 `account_type = 'BANK'`。

## 需求背景

企业账户按类型区分，普通银行账户用于日常结算。系统依据该口径进行账户类型筛选和路由。

## 版本演进

基于数据库证据建立本口径 v0。

```ground:caliber
name: 普通银行账户
predicate: "cust_account_info.account_type = 'BANK'"
scope: 企业录入的一般银行结算账户
evidence: db
```

[[cust_account_info]] 表字段 `account_type` 承载该类型口径。