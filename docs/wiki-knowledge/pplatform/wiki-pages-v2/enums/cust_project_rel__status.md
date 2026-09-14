---
type: enum
title: status
page_key: cust_project_rel__status
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

（权威枚举页：3 值，绑定方式 db-profile，主承载 cust_project_rel.status；db 实测分布。）

```ground:enum
enum: cust_project_rel__status
fields: [cust_project_rel.status]
values:
  " 1 ":
    label: "1"
  "0":
    label: "否"
  "1":
    label: "是"
```
