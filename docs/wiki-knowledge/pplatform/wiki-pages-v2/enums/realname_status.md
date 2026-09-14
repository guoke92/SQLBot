---
type: enum
title: realname_status
page_key: realname_status
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




# realname_status

（权威枚举页：4 值，绑定方式 db-profile，主承载 cust_person_info.realname_status；db 实测分布。）

```ground:enum
enum: realname_status
fields: [cust_person_info.realname_status]
values:
  "AUTOMATIC_AUTHENTICATION_FAILED":
    label: "AUTOMATIC_AUTHENTICATION_FAILED"
  "AUTOMATIC_AUTHENTICATION_PASSED":
    label: "AUTOMATIC_AUTHENTICATION_PASSED"
  "MANUAL_AUTHENTICATION_PASSED":
    label: "MANUAL_AUTHENTICATION_PASSED"
  "TO_BE_VERIFIED":
    label: "TO_BE_VERIFIED"
```
