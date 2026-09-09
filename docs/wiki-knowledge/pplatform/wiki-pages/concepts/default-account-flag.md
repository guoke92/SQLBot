---
type: concept
title: 默认还款账号
page_key: default-account-flag
belong: concepts
domain: 企业银行账户与第三方银行
status: published
aliases: ["默认账户", "defaultAccountFlag", "default_account_flag"]
oid: 1
sources: ["db", "code"]
contract_version: "0.1"
maps_to: "cust_account_info.default_account_flag = '1'"
field_targets: ["cust_account_info.default_account_flag"]
adjudication: synonym
also_confused_with: ["账户类型账户类型"]
boundary: "同一企业下仅一条 default_account_flag='1'"
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

术语“默认还款账号”指企业用于还款业务的首选银行账户。该术语桥将业务词汇映射到字段 `cust_account_info.default_account_flag = '1'`，并明确其唯一性边界。

## 需求背景

还款业务需要确定一个明确的入账账户。业务术语“默认还款账号”在代码和数据库中以 `default_account_flag` 字段的 `'1'` 值表达。系统通过该映射识别默认账户，并确保同一企业下仅一条记录满足条件。

## 版本演进

本概念契约 v0 基于语义分析建立，将业务术语与物理字段关联，防止与“账户类型”等概念混淆。

[[cust_account_info]] 表字段 `default_account_flag` 是该概念的物理承载。