---
type: rule
title: 打款次数配额
page_key: rules/payment-count-quota
domain: 企业银行账户
status: draft
aliases: [剩余打款次数, payment_remaining_count]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustAccountApplication.java:cnapsPaymentApply
  - code_path:CustAccountApplication.java:updatePayCount
contract_version: "0.1"
---

限制单个账户发起小额打款频次的规则：剩余次数初始取自配置、每次申请成功后扣减、为 0 时阻断。语境见 [[processes/account-cnaps-payment-auth-state]]。

## 需求背景

打款涉及真实资金与银行接口调用，需要频次刹车防止滥用与重复试探；配置项 `cust_setting_config.payment_maximum_number` 提供上限来源，账户侧记录剩余量。

## 版本演进

v0 契约按现状固化；剩余次数按账户维度维护，配置变更不影响已初始化账户的剩余值。

## 规则锚点

```ground:rule
name: 打款次数配额
content: 剩余打款次数初始值取自 cust_setting_config.payment_maximum_number（updatePayCount）；每次申请打款成功后 -1；为 0 时抛“今天打款次数已用完，请明天再试”。
impact: 限制账户验证频率
field_targets:
  - cust_account_info.payment_remaining_count
  - cust_setting_config.payment_maximum_number
evidence: code_path:CustAccountApplication.java:cnapsPaymentApply / updatePayCount
```