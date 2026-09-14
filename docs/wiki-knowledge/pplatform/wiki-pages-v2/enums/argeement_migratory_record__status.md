---
type: enum
title: status
page_key: argeement_migratory_record__status
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




# status

（权威枚举页：2 值，绑定方式 db-profile，主承载 argeement_migratory_record.status；db 实测分布。）

```ground:enum
enum: argeement_migratory_record__status
fields: [argeement_migratory_record.status]
values:
  "0":
    label: "否"
  "1":
    label: "是"
```
