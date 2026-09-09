---
type: concept
title: 账户账号
page_key: account-no
belong: concepts
domain: 企业银行账户与第三方银行
status: published
aliases: ["accountNo", "account_no", "accountNumber"]
oid: 1
sources: ["db", "code"]
contract_version: "0.1"
maps_to: "cust_account_info.account_no"
field_targets: ["cust_account_info.account_no"]
adjudication: boundary
also_confused_with: ["银行账户名称 account_name"]
boundary: "account_no为账号，account_name为账户名称"
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

术语“账户账号”指银行账户的账号数字，是打款验证入账账号。该术语桥映射到 `cust_account_info.account_no`，并与账户名称区分。

## 需求背景

企业账户录入时，需要区分账号与账户名称。账号用于资金转移，账户名称用于显示。该术语桥消除两者混淆。

## 版本演进

本概念契约 v0 基于数据库与代码证据建立。

[[cust_account_info]] 表字段 `account_no` 是该概念的物理承载。