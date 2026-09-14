---
type: rule
title: 账户不可重复添加
page_key: account_no_unique
domain: 企业银行账户
status: draft
aliases:
  - 账号去重规则
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
belong: rules
---

# 账户不可重复添加

新增账户前，在同一归属企业内校验 `account_no` 是否已存在，命中即拒绝并提示“账户不能重复添加”。

## 需求背景

账户档案需要避免同一企业下重复登记同一银行账号，否则默认账户、打款次数、认证状态会出现多条并行记录。表结构见 [[cust_account_info]]。

## 版本演进

- 校验在 `checkBefore` 中完成，属前置校验，非数据库唯一约束。

```ground:rule
name: 账户不可重复添加
content: 同一归属企业内相同 account_no 唯一，命中时报“账户不能重复添加”
impact: 阻断新增
field_targets:
  - cust_account_info.account_no
  - cust_account_info.ref_cust_company_info
evidence: code_path:CustAccountApplication.java:checkBefore
```