---
type: enum
title: top_flag
page_key: top_flag
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


# top_flag

（权威枚举页：2 值，绑定方式 db-profile，主承载 cust_project_rel.top_flag；db 实测分布。）

```ground:enum
enum: top_flag
fields: [cust_project_rel.top_flag]
values:
  "0":
    label: "否"
  "1":
    label: "是"
```
