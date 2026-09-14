---
type: rule
title: 验证失败计数口径
page_key: payment-fail-count
domain: 企业银行账户
status: draft
aliases: [error_try_count, 验证失败累加]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustAccountApplication.java:cnapsPaymentConfirm
contract_version: "0.1"
belong: rules
---

打款金额验证失败时的记录规则：金额不匹配或银行库无记录时，先落状态再累加失败次数与时间，最后抛业务异常。直接决定 [[calibers/account-payment-auth-passed]] 的可用性。

## 需求背景

失败需要留痕以支持人工排查与风控（疑似恶意试探），同时失败请求本身也需要把账户推进到终态避免重复卡在 APPLY_20。

## 版本演进

v0 契约按现状固化，并由此产生一个已知口径缺陷：失败请求同样落 APPLY_40，故该状态不等于验证通过，需结合 error_try_count 判读。

## 规则锚点

```ground:rule
name: 验证失败计数口径
content: 金额不匹配（result=1）或银行库无记录（result=2）时，先置 auth_state=APPLY_40，再 error_try_count+1、error_try_time=now，然后抛业务异常——失败请求也会留下 APPLY_40 状态。
impact: auth_state=APPLY_40 不能单独作为“验证通过”口径，需结合 error_try_count 判断
field_targets:
  - cust_account_info.auth_state
  - cust_account_info.error_try_count
  - cust_account_info.error_try_time
evidence: code_path:CustAccountApplication.java:cnapsPaymentConfirm
```