---
type: enum
title: alter_mode
page_key: alter_mode
domain: 基线
status: draft
aliases: []
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]
created: '2026-09-10'
updated: '2026-09-10'
contract_version: "0.1"
---

# alter_mode

（权威枚举页：2 值，绑定方式 exact-name，主承载 cust_change_record.alter_mode；db 实测分布。）

```ground:enum
enum: alter_mode
fields: [cust_change_record.alter_mode]
values:
  1:
    label: 平台变更
  2:
    label: 企业自行变更
```
