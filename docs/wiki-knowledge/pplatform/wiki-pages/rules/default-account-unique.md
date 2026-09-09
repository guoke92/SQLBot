---
type: rule
title: 默认还款账号唯一
page_key: default-account-unique
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

规则“默认还款账号唯一”确保同一时刻一个企业只有一个默认还款账户。设置默认账户时，先清除原默认标识，再设置新账户。

## 需求背景

企业有多个账户时，默认账户必须唯一。该规则在 `setDefaultFlag` 方法中实现，避免出现多个默认账户导致还款混乱。

## 版本演进

基于代码证据建立规则 v0。

```ground:rule
name: 默认还款账号唯一
content: 设置默认账户时，先将原默认账户 default_account_flag 置 0，再将目标账户置 1
impact: 一个企业同一时刻只能有一个默认还款账号
field_targets:
  - cust_account_info.default_account_flag
evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:setDefaultFlag"
```

[[cust_account_info]] 表字段 `default_account_flag` 参与该规则。