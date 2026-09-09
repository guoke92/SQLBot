---
type: rule
title: 打款验证前置状态校验
page_key: payment-confirm-precheck
belong: rules
domain: 企业银行账户与第三方银行
status: published
aliases: []
oid: 1
sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_account_info.auth_state]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

规则“打款验证前置状态校验”在用户确认金额前刷新状态，并校验是否为可验证状态：`APPLY_10` 或 `APPLY_30` 时阻止确认。

## 需求背景

不是所有状态都允许确认金额。该规则确保只有在银行受理成功（`APPLY_20`）后才能进行验证确认，避免无效操作。

## 版本演进

基于代码证据建立规则 v0。

```ground:rule
name: 打款验证前置状态校验
content: 确认金额前调用 paymentResult 刷新状态；如为APPLY_10提示未受理成功，如为APPLY_30提示申请受理失败需重新申请
impact: 阻止在非可验证状态确认
field_targets:
  - cust_account_info.auth_state
evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:cnapsPaymentConfirm"
```

[[cust-account-info-auth-state]] 状态机中的确认事件受此规则约束。

相关：[[cust_account_info]]
