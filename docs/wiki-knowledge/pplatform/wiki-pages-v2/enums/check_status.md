---
type: enum
title: check_status
page_key: check_status
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




# check_status

（权威枚举页：6 值，绑定方式 db-profile，主承载 cust_company_info.check_status；db 实测分布。）

```ground:enum
enum: check_status
fields: [cust_company_info.check_status]
values:
  "CUST_CHECK_BACKTOCUSTOM":
    label: "CUST_CHECK_BACKTOCUSTOM"
  "CUST_CHECK_CHECKING":
    label: "CUST_CHECK_CHECKING"
  "CUST_CHECK_INIT":
    label: "CUST_CHECK_INIT"
  "CUST_CHECK_PASS":
    label: "CUST_CHECK_PASS"
  "CUST_CHECK_REJECT":
    label: "CUST_CHECK_REJECT"
  "EFFECT":
    label: "EFFECT"
```
