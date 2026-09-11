---
type: rule
title: 验证前置状态约束
page_key: rules/payment-confirm-precondition
domain: 企业银行账户
status: draft
aliases: [打款验证时序约束, cnapsPaymentConfirm 前置校验]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustAccountApplication.java:cnapsPaymentConfirm
contract_version: "0.1"
---

金额验证动作的时序约束规则：必须先申请打款、必须等银行受理成功，受理失败则需重新申请。状态取值见 [[processes/account-cnaps-payment-auth-state]]，交易标识要求见 [[concepts/trans-id-vs-trace-no]]。

## 需求背景

验证是与银行侧的一次比对动作，缺少 trans_id 或处于未受理/受理失败状态时调用必然失败并消耗配额，因此在服务层前置拦截并给出可操作提示。

## 版本演进

v0 契约按现状固化，三条前置条件共用同一入口校验。

## 规则锚点

```ground:rule
name: 验证前置状态约束
content: 无 trans_id 抛“请先发起申请打款”；auth_state=APPLY_10 抛“还未受理成功，请在账户收到打款金额后再验证”；auth_state=APPLY_30 抛“申请打款受理失败，请重新申请打款”。
impact: 打款验证时序约束
field_targets:
  - cust_account_info.trans_id
  - cust_account_info.auth_state
evidence: code_path:CustAccountApplication.java:cnapsPaymentConfirm
```