---
type: caliber
title: 默认还款账户
page_key: default-repayment-account
domain: 企业银行账户与第三方银行
status: published
aliases: ["默认账户", "default_account_flag"]
oid: 1
sources: ["code", "db"]
contract_version: "0.1"
field_targets: [cust_account_info.default_account_flag]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

口径“默认还款账户”用于判定一个企业下哪个银行账户作为默认还款账户。其判定条件为 `default_account_flag = '1'`，且在同一企业内唯一。

## 需求背景

企业可能存在多个银行账户，但还款业务需要指定唯一默认账户，避免资金分散。系统通过该口径识别默认账户，并在设置、保存、查询等场景中保持一致。

## 版本演进

本口径基于代码证据建立。当前 v0 明确同一企业唯一性约束。

```ground:caliber
name: 默认还款账户
predicate: "cust_account_info.default_account_flag = '1'"
scope: 同一企业（ref_cust_company_info）内唯一
evidence: code
```

[[cust_account_info]] 表字段 `default_account_flag` 是实现该口径的关键字段。