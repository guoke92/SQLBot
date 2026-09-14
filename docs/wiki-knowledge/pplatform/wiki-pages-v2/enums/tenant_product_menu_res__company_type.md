---
type: enum
title: company_type
page_key: tenant_product_menu_res__company_type
domain: 基线
status: draft
aliases: []
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: enums
---




# company_type

（权威枚举页：4 值，绑定方式 db-profile，主承载 tenant_product_menu_res.company_type；db 实测分布。）

```ground:enum
enum: tenant_product_menu_res__company_type
fields: [tenant_product_menu_res.company_type]
values:
  "CORE":
    label: "CORE"
  "CORPORATION_COMPANY":
    label: "CORPORATION_COMPANY"
  "PLATFORM_OPERATOR_COMPANY":
    label: "PLATFORM_OPERATOR_COMPANY"
  "SUPPLIER":
    label: "SUPPLIER"
```
