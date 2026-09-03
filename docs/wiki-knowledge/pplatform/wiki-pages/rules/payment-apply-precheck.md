---
type: rule
title: 打款申请前置校验
page_key: payment-apply-precheck
domain: 企业银行账户与第三方银行
status: published
aliases: []
oid: 1
sources: ["code"]
contract_version: "0.1"
field_targets: [cust_account_info.account_name, cust_account_info.account_no, cust_account_info.bank_no, cust_account_info.payment_remaining_count]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

规则“打款申请前置校验”在发起打款申请前检查必要信息和剩余次数，缺失或次数为零时阻断申请。

## 需求背景

打款申请需要账户账号、名称、联行号等关键信息，且剩余次数必须大于 0。该规则确保申请条件满足，避免无效调用银行接口。

## 版本演进

基于代码证据建立规则 v0。

```ground:rule
name: 打款申请前置校验
content: 申请打款前需账户 account_no、account_name、bank_no 均不为空，且 payment_remaining_count > 0
impact: 必要信息缺失或次数用完时阻断申请
field_targets:
  - cust_account_info.account_no
  - cust_account_info.account_name
  - cust_account_info.bank_no
  - cust_account_info.payment_remaining_count
evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:cnapsPaymentApply"
```

[[cust_account_info]] 表字段 `account_no`、`account_name`、`bank_no`、`payment_remaining_count` 参与该规则。