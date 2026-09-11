---
type: enum
title: product_status
page_key: product_status
domain: 基线
status: draft
aliases: []
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]
created: '2026-09-10'
updated: '2026-09-10'
contract_version: "0.1"
---

# product_status

（权威枚举页：2 值，绑定方式 setter-evidence，主承载 platform_product.product_status；db 实测分布。）

```ground:enum
enum: product_status
fields: [platform_product.product_status]
values:
  0:
    label: 待生效
  1:
    label: 已生效
```
