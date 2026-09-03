---
type: rule
title: 打款申请成功后处理
page_key: payment-apply-success
domain: 企业银行账户与第三方银行
status: published
aliases: []
oid: 1
sources: ["code"]
contract_version: "0.1"
field_targets: [cust_account_info.auth_state, cust_account_info.payment_remaining_count, cust_account_info.trace_no, cust_account_info.trans_id]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

规则“打款申请成功后处理”在银行返回成功后更新账户状态：扣减剩余次数、记录交易ID与跟踪号，并将认证状态置为 `APPLY_10`。

## 需求背景

申请成功后，账户进入“已申请待查询”状态。记录银行返回的流水号便于后续查询，扣减次数防止超限。

## 版本演进

基于代码证据建立规则 v0。

```ground:rule
name: 打款申请成功后处理
content: 银行返回成功后，扣减剩余次数，记录 trans_id/trace_no，设置 auth_state=APPLY_10
impact: 账户进入已申请待查询状态
field_targets:
  - cust_account_info.payment_remaining_count
  - cust_account_info.trans_id
  - cust_account_info.trace_no
  - cust_account_info.auth_state
evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:cnapsPaymentApply"
```

[[cust_account_info]] 表字段 `payment_remaining_count`、`trans_id`、`trace_no`、`auth_state` 参与该规则。