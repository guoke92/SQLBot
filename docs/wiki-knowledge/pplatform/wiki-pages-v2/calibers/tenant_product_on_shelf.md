---
type: caliber
title: 租户产品已上架
page_key: tenant_product_on_shelf
domain: 平台产品配置
status: draft
aliases: [租户产品已开通, open_status=Y]
oid: 1
scope:
  databases: [platform]
sources:
  - code
contract_version: "0.1"
belong: calibers
---

「租户产品已上架」是开通客户产品的前置校验口径，也是租户产品列表的可见条件，等价于 [[tenant_product]] 的 `open_status = 'Y'`。

## 需求背景

客户产品开通（[[cust_product_opening]]）前必须命中该口径；处理中的 P 值需等待多级回调（[[multi_level_callback_pending]]），流转见 [[tenant_product_open_status]]。

## 版本演进

- 初版口径；需求文档所述 ACTIVE 字面量与实现不符，实际为 `'Y'`。

```ground:caliber
name: 租户产品已上架
predicate: "tenant_product.open_status = 'Y'"
scope: 开通客户产品前置校验/租户产品列表
evidence: code
```

关联：[[tenant_product]]、[[tenant_product_open_status]]、[[multi_level_callback_pending]]