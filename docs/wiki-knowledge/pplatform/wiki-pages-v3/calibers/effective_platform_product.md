---
type: caliber
title: 已生效平台产品
page_key: effective_platform_product
domain: 平台产品配置
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: calibers
field_targets:
  - platform_product.product_status
---

dictKey `'1'` = 已生效。

```ground:caliber
name: 已生效平台产品
predicate: "platform_product.product_status = '1'"
scope: platform_product
evidence: code
```
