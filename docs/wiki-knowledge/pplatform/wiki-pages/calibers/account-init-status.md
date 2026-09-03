---
type: caliber
title: 账户初始化状态
page_key: account-init-status
domain: 企业银行账户与第三方银行
status: published
aliases: ["INIT", "初始状态"]
oid: 1
sources: ["db"]
contract_version: "0.1"
field_targets: [cust_account_info.status]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

口径“账户初始化状态”标识账户记录处于初始状态。其判定条件为 `status = 'INIT'`。

## 需求背景

账户记录创建后默认为初始状态，后续可能根据业务流程变更。该口径用于识别尚未进入后续处理的账户。

## 版本演进

基于数据库证据建立本口径 v0。

```ground:caliber
name: 账户初始化状态
predicate: "cust_account_info.status = 'INIT'"
scope: 账户记录初始状态
evidence: db
```

[[cust_account_info]] 表字段 `status` 承载该状态口径。