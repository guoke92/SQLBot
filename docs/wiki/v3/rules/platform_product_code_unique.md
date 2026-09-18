---
type: rule
title: 平台产品编码唯一
page_key: platform_product_code_unique
belong: rules
domain: remaining
status: draft
field_targets: [platform_product.product_code]
sources: ['code_path:PlatformProductDaoImpl.java:60']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [platform_product]
---

# 平台产品编码唯一

保存时按 product_code 查重。

```ground:rule
rule: 平台产品编码唯一
field_targets: [platform_product.product_code]
impact: write_constraint
content: 保存时按 product_code 查重。
evidence: code_path:PlatformProductDaoImpl.java:60
```

## 页面链接

- [[tables/platform_product]]
- [[dicts/platform_product__product_code]]
