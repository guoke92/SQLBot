---
type: caliber
title: 供应商企业
page_key: supplier-company
belong: calibers
domain: 企业建档与准入
status: published
aliases: [供应商]
oid: 1

sources: ["db", "code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_company_info.cust_company_type]
scope:
  databases: [lowcode_pplatform]
---

# 供应商企业

本口径识别企业角色包含供应商的企业，依据 `cust_company_info.cust_company_type` 中 JSON 数组包含 SUPPLIER 标记。常用于供应链准入、银行账户必填等场景。

## 需求背景

供应商企业在建档时需要满足额外的银行账户必填校验，见 [[supplier-bank-account-required]] 规则。企业角色由 [[enterprise-role]] 概念统一解释。

## 版本演进

口径证据来自代码 `CustCompanyTypeEnum.SUPPLIER` 对应 dictKey 为 'SUPPLIER'。

```ground:caliber
name: 供应商企业
predicate: "cust_company_info.cust_company_type LIKE '%SUPPLIER%'"
scope: 企业角色包含供应商
evidence: "code:CustCompanyTypeEnum.SUPPLIER 对应 dictKey 为 'SUPPLIER'"
```

相关概念：[[enterprise-role]]；相关规则：[[supplier-bank-account-required]]

相关：[[cust_company_info]]
