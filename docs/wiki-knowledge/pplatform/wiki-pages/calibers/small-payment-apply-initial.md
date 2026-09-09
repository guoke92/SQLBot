---
type: caliber
title: 小额打款验证申请初始态
page_key: small-payment-apply-initial
belong: calibers
domain: 企业银行账户与第三方银行
status: published
aliases: ["APPLY_00", "未申请打款"]
oid: 1
sources: ["db"]
contract_version: "0.1"
field_targets: [cust_account_info.auth_state]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

口径“小额打款验证申请初始态”标识账户尚未发起过打款验证。其判定条件为 `auth_state = 'APPLY_00'`。

## 需求背景

在小额打款验证流程中，初始态表示账户还未进入申请环节。系统通过该口径过滤可发起申请的账户，并限制重复申请。

## 版本演进

基于数据库字典证据建立本口径 v0。

```ground:caliber
name: 小额打款验证申请初始态
predicate: "cust_account_info.auth_state = 'APPLY_00'"
scope: 账户未发起打款验证
evidence: db
```

[[cust_account_info]] 表字段 `auth_state` 承载该状态口径。