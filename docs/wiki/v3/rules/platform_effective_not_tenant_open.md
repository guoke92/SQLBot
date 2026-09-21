---
type: rule
title: 平台产品生效不是租户开通
page_key: platform_effective_not_tenant_open
belong: rules
domain: remaining
status: draft
field_targets: [platform_product.product_status, tenant_product.open_status]
sources: ['code_path:PlatformProduct.java:100']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [platform_product, tenant_product]
---

# 平台产品生效不是租户开通

/platformProduct/effective 只写 product_status=1。不改 tenant_product.open_status。

```ground:rule
rule: 平台产品生效不是租户开通
field_targets: [platform_product.product_status, tenant_product.open_status]
impact: write_constraint
content: /platformProduct/effective 只写 product_status=1。不改 tenant_product.open_status。
evidence: code_path:PlatformProduct.java:100
```

## 页面链接

- [[tables/platform_product]]
- [[tables/tenant_product]]
- [[dicts/platform_product__product_status]]
- [[dicts/tenant_product__open_status]]
- [[processes/platform_product__product_status]]
- [[processes/tenant_product__open_status]]
