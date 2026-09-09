---
type: rule
title: 保存后自动补默认账户
page_key: auto-set-default-account
belong: rules
domain: 企业银行账户与第三方银行
status: published
aliases: []
oid: 1
sources: ["code"]
contract_version: "0.1"
field_targets: [cust_account_info.default_account_flag]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

规则“保存后自动补默认账户”保证企业至少存在一个默认账户。当保存后没有默认账户时，系统自动将当前账户设为默认。

## 需求背景

新增第一个账户后，企业需要默认账户用于后续还款操作。该规则在 `afterSave` 中执行，提升用户体验并确保业务可继续。

## 版本演进

基于代码证据建立规则 v0。

```ground:rule
name: 保存后自动补默认账户
content: 保存账户后如无默认账户，则自动将当前账户设为默认账户
impact: 保证企业至少存在一个默认账户
field_targets:
  - cust_account_info.default_account_flag
evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:afterSave"
```

[[cust_account_info]] 表字段 `default_account_flag` 参与该规则。