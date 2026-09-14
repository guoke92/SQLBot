---
type: enum
title: operator_ai_customer
page_key: operator_ai_customer
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




# operator_ai_customer

（权威枚举页：2 值，绑定方式 db-profile，主承载 tenant_setting_config.operator_ai_customer；db 实测分布。）

```ground:enum
enum: operator_ai_customer
fields: [tenant_setting_config.operator_ai_customer]
values:
  "0":
    label: "否"
  "1":
    label: "是"
```
