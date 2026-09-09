---
type: rule
title: 验证金额范围校验
page_key: payment-amount-range-check
belong: rules
domain: 企业银行账户与第三方银行
status: published
aliases: []
oid: 1
sources: ["code"]
contract_version: "0.1"
field_targets: [cust_account_info.auth_state]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

规则“验证金额范围校验”限制用户输入的验证金额必须大于 0 且小于 1（即 0.01~0.99），服务端将金额乘以 100 转化为分后传给银行。

## 需求背景

小额打款验证的金额是 0.01 到 0.99 元的小数。该规则在 controller 层进行校验，确保传入银行的数据格式正确。

## 版本演进

基于代码证据建立规则 v0。

```ground:rule
name: 验证金额范围校验
content: 前端传入验证金额必须大于0且小于1（0.01~0.99），服务端校验后乘以100转为分传给银行
impact: 限制小额打款金额范围
field_targets:
  - cust_account_info.auth_state
  - 打款验证金额
evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/CustAccountInfoController.java:paymentConfirm"
```

[[cust_account_info]] 表字段 `auth_state` 及验证金额输入参与该规则。