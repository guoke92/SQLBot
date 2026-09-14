---
type: enum
title: access_mode
page_key: access_mode
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




# access_mode

（权威枚举页：1 值，绑定方式 db-profile，主承载 tenant_setting_config.access_mode；db 实测分布。）

```ground:enum
enum: access_mode
fields: [tenant_setting_config.access_mode]
values:
  "DIRECT_INIT":
    label: "DIRECT_INIT"
```
