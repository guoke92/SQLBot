---
type: enum
title: rule_status
page_key: rule_status
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












# rule_status

（权威枚举页：3 值，绑定方式 setter-evidence，主承载 funding_rule_info.rule_status；db 实测分布。）

```ground:enum
enum: rule_status
fields: [funding_rule_info.rule_status]
values:
  "PENDING":
    label: "待生效"
  "ACTIVE":
    label: "生效中"
  "INACTIVE":
    label: "已失效"
```
