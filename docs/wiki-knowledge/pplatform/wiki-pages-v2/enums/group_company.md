---
type: enum
title: group_company
page_key: group_company
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




# group_company

（权威枚举页：3 值，绑定方式 db-profile，主承载 cust_company_info.group_company；db 实测分布。）

```ground:enum
enum: group_company
fields: [cust_company_info.group_company]
values:
  "1":
    label: "是"
  "N":
    label: "否"
  "Y":
    label: "是"
```
