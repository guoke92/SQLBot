---
type: rule
title: 打款次数用尽阻断
page_key: payment_count_exhausted
domain: 企业银行账户
status: draft
aliases:
  - 打款次数用完阻断
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
belong: rules
---

# 打款次数用尽阻断

`payment_remaining_count == 0` 时抛“今天打款次数已用完”，阻断打款申请；申请成功后剩余次数 -1。

## 需求背景

打款涉及真实资金与银行接口成本，需要对单账户的发起次数做上限控制，初始化规则见 [[payment_count_init]]。

## 版本演进

- 提示文案为“今天打款次数已用完”，但字段语义是“剩余可发起次数”并随申请递减，未见到按日重置逻辑的写值点，日切语义待确认。

```ground:rule
name: 打款次数用尽阻断
content: payment_remaining_count == 0 时抛“今天打款次数已用完”，申请成功后 -1
impact: 阻断
field_targets:
  - cust_account_info.payment_remaining_count
evidence: code_path:CustAccountApplication.java:cnapsPaymentApply
```