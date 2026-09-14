---
type: caliber
title: 客户产品未开通
page_key: cust_product_not_opened
domain: 平台产品配置
status: draft
aliases: [未开通产品, NOT_OPENED]
oid: 1
scope:
  databases: [platform]
sources:
  - code
contract_version: "0.1"
belong: calibers
---

「客户产品未开通」既表达记录初始态，也承担「查无授权记录」时的回退语义，等价于 [[cust_auth_application]] 的 `open_status = 'NOT_OPENED'`。

## 需求背景

租户产品未开通回退与展示均使用该口径；在 `listTenantProductWithOpenedCustProduct` 与 `queryProductStatus` 中作为默认值出现，见 [[cust_product_open_status]]。

## 版本演进

- 初版口径，同时作为默认回退值，无历史变更。

```ground:caliber
name: 客户产品未开通
predicate: "cust_auth_application.open_status = 'NOT_OPENED'"
scope: 租户产品未开通回退与展示
evidence: code
```

关联：[[cust_auth_application]]、[[cust_product_open_status]]、[[tenant_product_open_status]]