---
type: enum
title: pay_status
page_key: pay_status
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












# pay_status

（权威枚举页：2 值，绑定方式 setter-evidence，主承载 ca_fee_company.pay_status；db 实测分布。）

```ground:enum
enum: pay_status
fields: [ca_fee_company.pay_status]
values:
  "PAID":
    label: "已缴费"
  "UNPAID":
    label: "未缴费"
```
