---
type: rule
title: 默认账户唯一
page_key: default-account-unique
domain: 企业银行账户
status: draft
aliases: [默认账号唯一, setDefaultFlag]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustAccountApplication.java:setDefaultFlag
  - code_path:CustAccountApplication.java:afterSave
contract_version: "0.1"
belong: rules
---

设置默认账号时的排他性规则：先把该企业已有默认账户置为非默认，再置目标账户为默认；企业无默认账户时由 afterSave 兜底。对应口径见 [[calibers/default-repayment-account]]。

## 需求背景

下游资金动作按「默认账户」取单条记录，若同企业出现多条默认会导致取数不确定，故在写入路径与保存后路径双重保证唯一性。企业判定基于 [[concepts/account-owner-company]]。

## 版本演进

v0 契约按现状固化，写路径与兜底路径并存。

## 规则锚点

```ground:rule
name: 默认账户唯一
content: 设置默认账号时先查询该企业下 default_account_flag='1' 的记录并置为 '0'，再把目标账户置 '1'；保存后 afterSave 会在企业无默认账户时自动把首个账户置为默认。
impact: 企业默认还款账号口径
field_targets:
  - cust_account_info.default_account_flag
  - cust_account_info.ref_cust_company_info
evidence: code_path:CustAccountApplication.java:setDefaultFlag / afterSave
```