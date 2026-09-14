---
type: enum
title: client_type
page_key: cust_change_cfg__client_type
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


# client_type

（权威枚举页：2 值，绑定方式 exact-name，主承载 cust_change_cfg.client_type；db 实测分布。）

```ground:enum
enum: cust_change_cfg__client_type
fields: [cust_change_cfg.client_type, cust_company_info.client_type, org_manage.client_type]
values:
  "AGW":
    label: "AGW"
  "ACCOUNT_PRODUCT":
    label: "ACCOUNT_PRODUCT"
```
