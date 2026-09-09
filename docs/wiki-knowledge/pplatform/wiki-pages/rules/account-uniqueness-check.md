---
type: rule
title: 账户唯一性校验
page_key: account-uniqueness-check
belong: rules
domain: 企业银行账户与第三方银行
status: published
aliases: []
oid: 1
sources: ["code"]
contract_version: "0.1"
field_targets: [cust_account_info.account_no, cust_account_info.ref_cust_company_info]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

规则“账户唯一性校验”用于防止同一企业下重复添加相同银行账号。系统在账户新增前检查 `account_no` 是否已存在。

## 需求背景

企业录账时，重复账户会导致还款、打款等场景混乱。该规则在 `checkBefore` 方法中执行，确保同一企业下账号唯一。

## 版本演进

基于代码证据建立规则 v0。

```ground:rule
name: 账户唯一性校验
content: 同一企业下同一 account_no 不能重复添加，存在则提示账户不能重复添加
impact: 阻止重复银行账户录入
field_targets:
  - cust_account_info.account_no
  - cust_account_info.ref_cust_company_info
evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:checkBefore"
```

[[cust_account_info]] 表字段 `account_no` 和 `ref_cust_company_info` 参与该规则。