---
type: process
title: 平台产品状态
page_key: platform_product__product_status
belong: processes
domain: remaining
status: draft
anchors: [platform_product.product_status]
field_targets: [platform_product.product_status]
sources: ['code_path:PlatformProduct.java:100']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [platform_product]
---

# 平台产品状态

钉 platform_product.product_status。人工生效写 1。不要当成租户产品 open_status。


```ground:process
process: 平台产品状态
field: platform_product.product_status
entry: POST /app-web/platformProduct/effective
stages:
- stage: 生效
  transitions:
  - from: '0'
    event: effective
    to: '1'
    evidence: code_path:PlatformProduct.java:100
```

## 页面链接

- [[tables/platform_product]]
- [[dicts/platform_product__product_status]]
