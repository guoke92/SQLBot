---
type: caliber
title: 有效账户
page_key: valid_account
domain: 企业银行账户
status: draft
aliases:
  - 启用账户口径
  - enable=Y
oid: 1
scope:
  databases:
    - customer_management
sources:
  - db
contract_version: "0.1"
belong: calibers
---

# 有效账户

口径判断：`cust_account_info.enable = 'Y'`，即逻辑启用标识为启用的账户。

## 需求背景

账户使用范围统计以启用标识收口，停用账户不纳入可用账户集合。

## 版本演进

- 全表实测均为 `'Y'`，该口径目前不产生过滤差异；一旦出现 `'N'`，需确认是否配套停用功能与迁移写值点。

```ground:caliber
name: 有效账户
predicate: cust_account_info.enable = 'Y'
scope: 全表实测均为 Y
evidence: db
```