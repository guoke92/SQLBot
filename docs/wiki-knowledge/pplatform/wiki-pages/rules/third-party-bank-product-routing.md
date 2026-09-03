---
type: rule
title: 第三方银行产品路由
page_key: third-party-bank-product-routing
domain: 企业银行账户与第三方银行
status: published
aliases: []
oid: 1
sources: ["code"]
contract_version: "0.1"
field_targets: [cust_account_info.account_type]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

规则“第三方银行产品路由”规定查询银行账户类型或分页银行账户时，RPC 路由目标取决于 `productCode`。`queryBankAccountType` 与 `pageBankInfo` 均需要产品 code。

## 需求背景

第三方银行服务因产品不同路由到不同服务端。该规则在 client 层实现，确保按产品隔离银行账户查询，避免跨产品数据混淆。

## 版本演进

基于代码证据建立规则 v0。

```ground:rule
name: 第三方银行产品路由
content: 查询银行账户类型/分页银行账户时，RPC路由目标取决于 productCode，queryBankAccountType 与 pageBankInfo 均需要产品 code
impact: 按产品隔离第三方银行账户查询
field_targets:
  - cust_account_info.account_type
  - product_code
evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/client/cust/ClientQueryBankAccountTypeService.java:getAppId"
```

[[cust_account_info]] 表字段 `account_type` 和产品代码参与该路由规则。