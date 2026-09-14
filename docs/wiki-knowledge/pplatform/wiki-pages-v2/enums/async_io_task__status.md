---
type: enum
title: status
page_key: async_io_task__status
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

（权威枚举页：3 值，绑定方式 db-profile，主承载 async_io_task.status；db 实测分布。）

```ground:enum
enum: async_io_task__status
fields: [async_io_task.status]
values:
  "FAILED":
    label: "FAILED"
  "RUNNING":
    label: "RUNNING"
  "SUCCESS":
    label: "SUCCESS"
```
