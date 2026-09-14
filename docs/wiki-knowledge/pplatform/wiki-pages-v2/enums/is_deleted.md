---
type: enum
title: is_deleted
page_key: is_deleted
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




# is_deleted

（权威枚举页：2 值，绑定方式 db-profile，主承载 async_io_task.is_deleted；db 实测分布。）

```ground:enum
enum: is_deleted
fields: [async_io_task.is_deleted]
values:
  "0":
    label: "否"
  "1":
    label: "是"
```
