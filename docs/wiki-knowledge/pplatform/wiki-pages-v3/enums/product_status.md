---
type: enum
title: product_status
page_key: product_status
domain: 平台产品配置
status: draft
aliases: [已生效产品]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
related: [product_status_flow]
---

# product_status

`ProductStatusEnum` dictKey：`'0'` 待生效 / `'1'` 已生效。

```ground:enum
enum: product_status
fields:
  - platform_product.product_status
values:
  "0":
    label: "待生效"
  "1":
    label: "已生效"
```
