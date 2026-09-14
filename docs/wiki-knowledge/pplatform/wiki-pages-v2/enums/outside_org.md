---
type: enum
title: outside_org
page_key: outside_org
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




# outside_org

（权威枚举页：4 值，绑定方式 db-profile，主承载 cust_company_info.outside_org；db 实测分布。）

```ground:enum
enum: outside_org
fields: [cust_company_info.outside_org]
values:
  "0":
    label: "否"
  "1":
    label: "是"
  "N":
    label: "否"
  "Y":
    label: "是"
```
