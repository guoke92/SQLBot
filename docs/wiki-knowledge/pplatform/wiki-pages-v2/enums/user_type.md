---
type: enum
title: user_type
page_key: user_type
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


# user_type

（权威枚举页：3 值，绑定方式 setter-evidence，主承载 cust_person_info.user_type；db 实测分布。）

```ground:enum
enum: user_type
fields: [cust_person_info.user_type]
values:
  "accountAdmin":
    label: "管理员"
    java_name: "admin"
  "accountNormal":
    label: "经办人"
    java_name: "operator"
  "accountGuest":
    label: "游客"
    java_name: "guest"
```
