---
type: scenario
title: 平台产品目录
page_key: platform_product_catalog
belong: scenarios
domain: remaining
status: draft
aliases: [产品大类, 平台产品]
sources: ['code_path:l1_intermediate']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [platform_product, platform_product_cust_role]
---

# 平台产品目录

平台产品主数据。租户开通写 tenant_product.platform_product_id。问已生效用 effective_platform_product。

```ground:scenario
scenario: platform_product_catalog
hubs:
- table: platform_product
  role: master
shared:
- table: platform_product_cust_role
  role: roles
lifecycle:
- dict: platform_product__product_status
  process: platform_product__product_status
```

## 页面链接

- [[tables/platform_product]]
- [[tables/platform_product_cust_role]]
- [[dicts/platform_product__product_status]]
- [[processes/platform_product__product_status]]
