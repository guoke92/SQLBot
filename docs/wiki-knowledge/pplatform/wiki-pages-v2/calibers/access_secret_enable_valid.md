---
type: caliber
title: 接入密钥有效性
page_key: access_secret_enable_valid
domain: 准入接入
status: draft
aliases: [启用口径, enable='Y', 密钥有效性]
oid: 1
scope:
  databases: [lowcode_pplatform_customer]
sources:
  - "code: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValue"
contract_version: "0.1"
---

「接入密钥有效性」是准入校验的第一道口径：判定一条 [[tables/cust_access_secret]] 记录是否处于可用状态。口径为 `enable = 'Y'`，作用域限定在接入密钥查询环节。

需要注意的是，该口径只回答“密钥是否启用”，不回答“渠道是否存在”——渠道存在性由 [[calibers/channel_lookup]] 与 [[rules/channel_exists_and_enabled]] 共同约束；两者串联后，才能得出“某渠道当前可接入”的结论。术语边界见 [[concepts/enable]]。

## 需求背景

语义分析中的 `reqdoc_claims` 为空，本页暂无需求文档主张可锚定；口径定义来自 `CustAccessApplication.validateSetValue` 的代码证据。

## 版本演进

- v0.1（本页）：首版口径，来源为 `validateSetValue`。

```ground:caliber
name: 接入密钥有效性
predicate: "cust_access_secret.enable = 'Y'"
scope: 接入密钥查询
evidence: "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValue"
```