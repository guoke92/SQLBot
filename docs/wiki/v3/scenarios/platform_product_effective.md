---
type: scenario
title: 生效平台产品
page_key: platform_product_effective
belong: scenarios
domain: remaining
status: draft
sources: ['code_path:l1_intermediate']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [platform_product]
---

# 生效平台产品

生效平台产品

```ground:scenario
scenario: platform_product_effective
hubs:
- table: platform_product
  role: master
lifecycle:
- dict: platform_product__product_status
  process: platform_product__product_status
```

## 页面链接

- [[tables/platform_product]]
- [[dicts/platform_product__product_status]]
- [[processes/platform_product__product_status]]
