---
type: rule
title: 验证结果处理
page_key: payment-result-handling
belong: rules
domain: 企业银行账户与第三方银行
status: published
aliases: []
oid: 1
sources: ["code"]
contract_version: "0.1"
field_targets: [cust_account_info.auth_state, cust_account_info.error_try_count, cust_account_info.error_try_time]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

规则“验证结果处理”根据银行返回结果处理验证：结果 `0` 一致直接置 `APPLY_40`；结果 `1` 不匹配和结果 `2` 库无记录均置 `APPLY_40` 并增加错误次数、记录错误时间，同时抛出异常。

## 需求背景

验证结果需要区分成功与失败，并记录失败次数用于限制。该规则统一处理三种结果，确保终态一致。

## 版本演进

基于代码证据建立规则 v0。

```ground:rule
name: 验证结果处理
content: 结果0一致直接置APPLY_40；结果1不匹配和结果2库无记录均置APPLY_40并增加错误次数/记录错误时间，且抛出异常
impact: 完成账户验证终态并记录失败次数
field_targets:
  - cust_account_info.auth_state
  - cust_account_info.error_try_count
  - cust_account_info.error_try_time
evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:cnapsPaymentConfirm"
```

[[cust_account_info]] 表字段 `auth_state`、`error_try_count`、`error_try_time` 参与该规则。