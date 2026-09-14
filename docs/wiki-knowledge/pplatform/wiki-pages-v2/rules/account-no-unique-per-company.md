---
type: rule
title: 企业账户不可重复
page_key: account-no-unique-per-company
domain: 企业银行账户
status: draft
aliases: [账户重复校验, 账户不能重复添加]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustAccountApplication.java:checkBefore
contract_version: "0.1"
belong: rules
---

新增企业银行账户时的前置唯一性校验：同一企业下 `account_no` 已存在则阻断新增。涉及表见 [[tables/cust_account_info]]，企业关联语义见 [[concepts/account-owner-company]]。

## 需求背景

重复账号会导致打款认证与默认账户口径出现歧义（同一账号多行、默认标记分散），因此在写入前按企业维度判重。

## 版本演进

v0 契约按现状固化，校验在 checkBefore 中前置执行。

## 规则锚点

```ground:rule
name: 企业账户不可重复
content: 同一企业（ref_cust_company_info）下 account_no 已存在时抛“账户不能重复添加”，阻断新增。
impact: 新增账户前置校验
field_targets:
  - cust_account_info.account_no
  - cust_account_info.ref_cust_company_info
evidence: code_path:CustAccountApplication.java:checkBefore
```