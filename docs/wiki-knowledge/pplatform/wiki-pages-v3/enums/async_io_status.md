---
type: enum
title: async_io_status
page_key: async_io_status
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [导入任务]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
related: [async_io_task_flow]
---

# async_io_status

`AsyncIoTaskStatusEnum` 只有枚举名，接口注释列出 PENDING / RUNNING / SUCCESS / FAILED。

```ground:enum
enum: async_io_status
fields:
  - async_io_task.status
values:
  "PENDING": {}
  "RUNNING": {}
  "SUCCESS": {}
  "FAILED": {}
```
