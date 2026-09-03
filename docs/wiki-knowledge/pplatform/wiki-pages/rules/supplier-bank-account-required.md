---
type: rule
title: 供应商银行账户必填
page_key: supplier-bank-account-required
domain: 企业建档与准入
status: published
aliases: [供应商银行账户校验]
oid: 1

sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_account_info.account_name, cust_account_info.account_no, cust_account_info.bank_no]
scope:
  databases: [lowcode_pplatform]
---

# 供应商银行账户必填

本规则要求当企业角色为供应商时，银行账户名、账号、联行号必填，缺失字段抛出参数错误。

## 需求背景

供应商企业在资金结算场景必须提供完整的银行账户信息。该规则与 [[supplier-company]] 口径联动。

## 版本演进

证据来自代码路径 `CustAccessApplication.validateBank`。

```ground:rule
name: 供应商银行账户必填
content: 当企业角色为供应商时，银行账户名、账号、联行号必填
impact: 缺失字段抛出参数错误
field_targets:
  - cust_account_info.account_name
  - cust_account_info.account_no
  - cust_account_info.bank_no
evidence: "code_path:CustAccessApplication.validateBank"
```

相关口径：[[supplier-company]]

相关：[[cust_account_info]]
