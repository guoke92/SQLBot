---
type: caliber
title: 小额打款验证完成终态
page_key: small-payment-verify-final
belong: calibers
domain: 企业银行账户与第三方银行
status: published
aliases: ["APPLY_40", "验证完成"]
oid: 1
sources: ["db"]
contract_version: "0.1"
field_targets: [cust_account_info.auth_state]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

口径“小额打款验证完成终态”标识账户的打款验证流程已终止。其判定条件为 `auth_state = 'APPLY_40'`，包含验证通过与验证失败两种情况。

## 需求背景

打款验证无论成功或失败，都会进入终态 `APPLY_40`。系统据此口径判断账户是否已完成验证，并阻止重复验证或进一步操作。

## 版本演进

基于数据库字典证据建立本口径 v0。

```ground:caliber
name: 小额打款验证完成终态
predicate: "cust_account_info.auth_state = 'APPLY_40'"
scope: 账户打款验证已完成（含成功与失败验证记录）
evidence: db
```

[[cust_account_info]] 表字段 `auth_state` 承载该状态口径。