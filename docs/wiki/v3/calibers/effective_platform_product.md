---
type: caliber
title: 已生效平台产品
page_key: effective_platform_product
belong: calibers
domain: remaining
status: draft
field_targets: [platform_product.product_status, platform_product.enable]
sources: ['code_path:PlatformProductDaoImpl.java:111']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [platform_product]
---

# 已生效平台产品

列表 listPlatformProduct 还可能再按 product_type 过滤。不要和租户产品 open_status 混用。

```ground:caliber
caliber: 已生效平台产品
field_targets: [platform_product.product_status, platform_product.enable]
predicate: platform_product.product_status = '1' AND platform_product.enable = 'Y'
scope: global
boundary: 列表 listPlatformProduct 还可能再按 product_type 过滤。不要和租户产品 open_status 混用。
using_relations: []
evidence: code_path:PlatformProductDaoImpl.java:111
```

## 页面链接

- [[tables/platform_product]]
- [[dicts/platform_product__enable]]
- [[dicts/platform_product__product_status]]
- [[processes/platform_product__product_status]]
