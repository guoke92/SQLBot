---
type: enum
title: sign_mode
page_key: sign_mode
domain: 授权协议与电子授权
status: draft
aliases: [线上签署]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# sign_mode

`SignModeEnum`。

```ground:enum
enum: sign_mode
fields:
  - argeement_migratory_record.sign_mode
values:
  "01":
    label: "线上"
  "02":
    label: "线下"
  "03":
    label: "无需签署"
```
