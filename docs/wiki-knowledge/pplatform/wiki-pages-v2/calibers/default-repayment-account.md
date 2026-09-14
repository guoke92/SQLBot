---
type: caliber
title: 默认还款账户口径
page_key: default-repayment-account
domain: 企业银行账户
status: draft
aliases: [默认账户, default_account_flag=1]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustAccountApplication.java:setDefaultFlag/afterSave
contract_version: "0.1"
belong: calibers
---

默认还款账户指企业名下被标记为默认的资金账户，是代扣/还款类业务的取数入口。判定条件为 `cust_account_info.default_account_flag = '1'`，作用域为同一归属企业；维护规则见 [[rules/default-account-unique]]。

## 需求背景

一个企业可绑定多个银行账户（[[tables/cust_account_info]]），但资金动作只能落到一个账户上，因此需要「默认标记 + 同企业唯一」的显式口径，避免下游按时间或主键取到不确定账户。企业名下无默认账户时，系统按 afterSave 逻辑自动把首个账户置为默认，保证口径恒有取值。

## 版本演进

v0 契约按现状固化。该口径同时被写入路径（setDefaultFlag 先清零再置一）与兜底路径（afterSave）维护，两条路径共同保证同企业唯一性。

## 口径锚点

```ground:caliber
name: 默认还款账户
predicate: cust_account_info.default_account_flag = '1'
scope: 同一 ref_cust_company_info 企业下唯一
evidence: code_path:CustAccountApplication.java:setDefaultFlag/afterSave
```