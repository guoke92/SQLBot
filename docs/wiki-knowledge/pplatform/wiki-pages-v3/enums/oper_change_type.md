---
type: enum
title: oper_change_type
page_key: oper_change_type
domain: 企业变更与运营变更
status: draft
aliases: [批量变更]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# oper_change_type

`OperChangeRecordApplication.CHANGE_TYPE_DESC`。

```ground:enum
enum: oper_change_type
fields:
  - cust_oper_change_record.change_type
values:
  "MANUAL":
    label: "手动变更"
  "BATCH":
    label: "批量变更"
  "AUTO_ASSIGN":
    label: "自动分配"
  "AUTO_UPDATE":
    label: "自动更新"
  "ASSET_AUDIT_SYNC":
    label: "资产审核同步"
  "CUST_CHANGE_CALLBACK":
    label: "企业变更回调"
```
