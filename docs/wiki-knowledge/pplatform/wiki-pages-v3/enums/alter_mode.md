---
type: enum
title: alter_mode
page_key: alter_mode
domain: 企业变更与运营变更
status: draft
aliases: [变更方式]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:AlterModeEnum.java", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# alter_mode

[[cust_change_record]] 的 `alter_mode`。`AlterModeEnum`：dictKey 为 `1`/`2`（不是枚举名 PLAT_ALTER）。

```ground:enum
enum: alter_mode
fields: [cust_change_record.alter_mode]
values:
  "1":
    label: "平台变更"
  "2":
    label: "企业自行变更"
```
