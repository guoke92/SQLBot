---
type: caliber
title: 企业自行变更单
page_key: self_alter_change
domain: 企业变更与运营变更
status: draft
aliases: [SELF_ALTER]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:AlterModeEnum.java"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: calibers
field_targets: [cust_change_record.alter_mode]
---

列在 [[cust_change_record]]。`alter_mode` 落库是 `'2'`，不是枚举名 `SELF_ALTER`。

```ground:caliber
name: 企业自行变更单
predicate: "cust_change_record.alter_mode = '2'"
scope: cust_change_record
evidence: code
```
