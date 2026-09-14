---
type: rule
title: 打款验证金额范围与单位
page_key: payment-amount-range
domain: 企业银行账户
status: draft
aliases: [验证金额0.01-0.99, checkAmount]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustAccountController.java:checkAmount
  - code_path:CustAccountController.java:cnapsPaymentConfirm
contract_version: "0.1"
belong: rules
---

打款金额验证的输入口径规则：金额必填、格式合法且严格落在 0 与 1 之间，上送银行前换算为「分」。语境见 [[processes/account-cnaps-payment-auth-state]]。

## 需求背景

小额打款金额以元为单位录入、以分为单位上送，若不做范围与单位约束，会出现「1 元打款」或单位不一致导致银行侧比对失败，进而污染失败次数（[[rules/payment-fail-count]]）。

## 版本演进

v0 契约按现状固化，控制器层统一承担范围与格式校验。

## 规则锚点

```ground:rule
name: 打款验证金额范围与单位
content: 控制器校验金额为空/格式错误即抛错，且必须 0 < amount < 1（提示“输入验证金额需要在0.01～0.99”）；上送银行前金额 *100 转为“分”。
impact: 小额打款验证输入口径
field_targets:
  - cust_account_info.auth_state
evidence: code_path:CustAccountController.java:checkAmount / cnapsPaymentConfirm
```