---
type: enum
title: default_account_flag
page_key: default_account_flag
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




# default_account_flag

（权威枚举页：2 值，绑定方式 db-profile，主承载 cust_account_info.default_account_flag；db 实测分布。）

```ground:enum
enum: default_account_flag
fields: [cust_account_info.default_account_flag]
values:
  "0":
    label: "否"
  "1":
    label: "是"
```
