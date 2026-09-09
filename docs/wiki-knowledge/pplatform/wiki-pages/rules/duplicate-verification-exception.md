---
type: rule
title: 重复验证异常兜底
page_key: duplicate-verification-exception
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

规则“重复验证异常兜底”处理银行返回的重复验证错误：若为已验证通过不能重复验证，则抛出“不能重复验证”；其他异常统一抛出“验证异常！”。

## 需求背景

重复验证时银行会返回错误信息，系统需要给出友好提示。该规则统一异常处理，避免暴露底层异常细节。

## 版本演进

基于代码证据建立规则 v0。

```ground:rule
name: 重复验证异常兜底
content: 银行返回“已验证通过，不能重复验证”时抛出“不能重复验证”，其他异常抛出“验证异常！”
impact: 防止重复验证并统一异常提示
field_targets:
  - cust_account_info.auth_state
evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:cnapsPaymentConfirm"
```

[[cust_account_info]] 表字段 `auth_state` 承载该规则触发的状态保护。