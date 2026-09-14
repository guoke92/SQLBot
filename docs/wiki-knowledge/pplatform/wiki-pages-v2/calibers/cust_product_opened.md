---
type: caliber
title: 客户产品已开通
page_key: cust_product_opened
domain: 平台产品配置
status: draft
aliases: [已开通产品, OPENED]
oid: 1
scope:
  databases: [platform]
sources:
  - code
contract_version: "0.1"
belong: calibers
---

「客户产品已开通」是客户端已开通产品列表、进入产品校验与 `queryProductStatus` 默认判活的统一判据，等价于 [[cust_auth_application]] 中该「企业 × 产品」记录的 `open_status` 为 OPENED。

## 需求背景

进入产品、展示「我的产品」、判断产品可用性均以该口径为准；未命中时按 [[cust_product_not_opened]] 回退展示。状态写入路径见 [[cust_product_open_status]]。

## 版本演进

- 初版口径，与常量类写值点一致，无历史变更。

```ground:caliber
name: 客户产品已开通
predicate: "cust_auth_application.open_status = 'OPENED'"
scope: 客户端已开通产品列表/进入产品校验/queryProductStatus 默认判活
evidence: code
```

关联：[[cust_auth_application]]、[[cust_product_open_status]]、[[product_open_status]]