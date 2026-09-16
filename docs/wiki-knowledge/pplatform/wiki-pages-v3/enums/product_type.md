---
type: enum
title: product_type
page_key: product_type
domain: 平台产品配置
status: draft
aliases: [通用产品, 互通产品]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# product_type

`PlatformProductTypeEnum`：GENERAL 通用产品 / INTERWORKING 互通产品 / ALL 的 dictKey 为 `'2'` 全部产品。

```ground:enum
enum: product_type
fields:
  - platform_product.product_type
values:
  "GENERAL":
    label: "通用产品"
  "INTERWORKING":
    label: "互通产品"
  "2":
    label: "全部产品"
```
