---
type: caliber
title: 手续费账户
page_key: operation-fee-account
domain: 企业银行账户与第三方银行
status: published
aliases: ["OPERATION_FEE_ACCOUNT", "手续费户"]
oid: 1
sources: ["db"]
contract_version: "0.1"
field_targets: [cust_account_info.account_type]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

口径“手续费账户”用于识别第三方银行或交e保服务费虚拟户等特殊账户。其判定条件为 `account_type = 'OPERATION_FEE_ACCOUNT'`。

## 需求背景

部分银行或第三方服务要求使用专门账户处理手续费。该口径将此类账户与普通银行账户区分，便于业务隔离。

## 版本演进

基于数据库证据建立本口径 v0。

```ground:caliber
name: 手续费账户
predicate: "cust_account_info.account_type = 'OPERATION_FEE_ACCOUNT'"
scope: 第三方银行/交e保服务费虚拟户等特殊账户
evidence: db
```

[[cust_account_info]] 表字段 `account_type` 承载该类型口径。