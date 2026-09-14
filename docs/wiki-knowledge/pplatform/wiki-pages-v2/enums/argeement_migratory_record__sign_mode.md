---
type: enum
title: sign_mode
page_key: argeement_migratory_record__sign_mode
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


# sign_mode

（权威枚举页：3 值，绑定方式 exact-name，主承载 argeement_migratory_record.sign_mode；db 实测分布。）

```ground:enum
enum: argeement_migratory_record__sign_mode
fields: [argeement_migratory_record.sign_mode]
values:
  "01":
    label: "线上"
    java_name: "ON_LINE"
  "02":
    label: "线下"
    java_name: "OFF_LINE"
  "03":
    label: "无需签署"
    java_name: "NO_SIGN"
```
