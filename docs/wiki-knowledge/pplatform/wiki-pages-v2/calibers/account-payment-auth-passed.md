---
type: caliber
title: 账户打款认证通过口径
page_key: account-payment-auth-passed
domain: 企业银行账户
status: draft
aliases: [认证通过账户, APPLY_40]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustAccountApplication.java:cnapsPaymentConfirm
contract_version: "0.1"
belong: calibers
---

账户打款认证通过指该银行账户已走完人行小额打款验证流程，判定条件为 `cust_account_info.auth_state = 'APPLY_40'`，作用域为账户维度。

## 需求背景

资金类业务只能使用经验证的真实账户，因此需要以认证状态作为准入口径。但现行实现中 APPLY_40 是「验证动作已终态」的标记，而非严格意义的「验证成功」，见 [[processes/account-cnaps-payment-auth-state]] 与 [[rules/payment-fail-count]]。

## 版本演进

v0 契约按现状固化。该口径当前不足以单独作为「验证通过」的过滤条件：建议配合 error_try_count 与 trans_id 组合判断，后续版本再决定是否拆出独立的成功状态。

## 口径锚点

```ground:caliber
name: 账户打款认证通过
predicate: cust_account_info.auth_state = 'APPLY_40'
scope: 账户维度
evidence: code_path:CustAccountApplication.java:cnapsPaymentConfirm
```