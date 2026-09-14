---
type: enum
title: max_financing_amount_flag
page_key: max_financing_amount_flag
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




# max_financing_amount_flag

（权威枚举页：4 值，绑定方式 db-profile，主承载 tenant_product.max_financing_amount_flag；db 实测分布。）

```ground:enum
enum: max_financing_amount_flag
fields: [tenant_product.max_financing_amount_flag]
values:
  "0":
    label: "否"
  "1":
    label: "是"
  "N":
    label: "否"
  "Y":
    label: "是"
```
