---
type: enum
title: customer_card_type
page_key: customer_card_type
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




# customer_card_type

（权威枚举页：2 值，绑定方式 db-profile，主承载 tenant_setting_config.customer_card_type；db 实测分布。）

```ground:enum
enum: customer_card_type
fields: [tenant_setting_config.customer_card_type]
values:
  "WX":
    label: "WX"
  "WX_WORK":
    label: "WX_WORK"
```
