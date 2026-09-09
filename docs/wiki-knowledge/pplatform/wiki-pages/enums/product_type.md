---
type: enum
title: product_type
page_key: product_type
belong: enums
domain: 基线
status: draft
aliases: []
oid: 1
sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# product_type

（权威枚举页：3 值，绑定方式 prefix-strip，主承载 platform_product.product_type；db 实测分布。）

```ground:enum
enum: product_type
fields: [platform_product.product_type, wechat_project_approval_apply.product_type]
values:
  GENERAL:
    label: 通用产品
  INTERWORKING:
    label: 互通产品
  2:
    label: 全部产品
```
