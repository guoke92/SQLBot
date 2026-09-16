---
type: enum
title: change_source
page_key: change_source
domain: 微企链立项与项目审批
status: draft
aliases: [同步保护]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# change_source

`ChangeSourceEnum` 无 displayName，中文取常量 Javadoc。非 SYNC 视为人工改过，同步 Job 不再覆盖。

```ground:enum
enum: change_source
fields:
  - wechat_project_approval_field_history.change_source
values:
  "EDIT":
    label: "详情页编辑保存"
  "BATCH":
    label: "批量变更"
  "IMPORT":
    label: "异步导入覆盖"
  "MANUAL_CREATE":
    label: "模拟立项时的初始写入"
  "SYNC":
    label: "企微小时同步 Job 写入"
```
