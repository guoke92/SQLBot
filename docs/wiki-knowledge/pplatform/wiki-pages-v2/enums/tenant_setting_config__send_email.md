---
type: enum
title: send_email
page_key: tenant_setting_config__send_email
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




# send_email

（权威枚举页：2 值，绑定方式 db-profile，主承载 tenant_setting_config.send_email；db 实测分布。）

```ground:enum
enum: tenant_setting_config__send_email
fields: [tenant_setting_config.send_email]
values:
  "0":
    label: "否"
  "1":
    label: "是"
```
