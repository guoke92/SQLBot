---
type: enum
title: key_type
page_key: key_type
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




# key_type

（权威枚举页：12 值，绑定方式 db-profile，主承载 funding_rule_front_cfg.key_type；db 实测分布。）

```ground:enum
enum: key_type
fields: [funding_rule_front_cfg.key_type]
values:
  "DATE_CHECK_NATURAL":
    label: "DATE_CHECK_NATURAL"
  "DATE_CHECK_WORKDAY":
    label: "DATE_CHECK_WORKDAY"
  "FIELD_LENGTH_LIMIT":
    label: "FIELD_LENGTH_LIMIT"
  "FIELD_REQUIRED":
    label: "FIELD_REQUIRED"
  "FILE_COUNT_LIMIT":
    label: "FILE_COUNT_LIMIT"
  "FILE_NAME_SYMBOL":
    label: "FILE_NAME_SYMBOL"
  "FILE_SIZE_PACKAGE_LIMIT":
    label: "FILE_SIZE_PACKAGE_LIMIT"
  "FILE_SIZE_SINGLE_LIMIT":
    label: "FILE_SIZE_SINGLE_LIMIT"
  "FILE_SIZE_TOTAL_LIMIT":
    label: "FILE_SIZE_TOTAL_LIMIT"
  "FILE_TYPE_LIMIT":
    label: "FILE_TYPE_LIMIT"
  "INVOICE_COUNT_LIMIT":
    label: "INVOICE_COUNT_LIMIT"
  "YEARS_CHECK":
    label: "YEARS_CHECK"
```
