---
type: caliber
title: 默认还款账户
page_key: default_repayment_account
domain: 企业银行账户
status: draft
aliases:
  - 默认账户口径
  - 默认还款账号
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
belong: calibers
---

# 默认还款账户

口径判断：`cust_account_info.default_account_flag = '1'`。语义为同一归属企业（`ref_cust_company_info`）下唯一的默认还款账户，由置默认与保存后逻辑互斥维护，术语辨析见 [[default_account]]。

## 需求背景

还款/扣款类业务需要明确“用哪个账户”，因此要求单企业唯一默认账户（[[single_default_account]]）。

## 版本演进

- 该口径由 `setDefaultFlag`/`afterSave` 维护，属写时维护型口径，不是查询时推导。

```ground:caliber
name: 默认还款账户
predicate: cust_account_info.default_account_flag = '1'
scope: 同一 ref_cust_company_info 下唯一；setDefaultFlag/afterSave 维护
evidence: code_path:CustAccountApplication.java:setDefaultFlag
```