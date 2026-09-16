---
type: enum
title: cust_source
page_key: cust_source
domain: 基线
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CustSourceEnum.java"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# cust_source

[[cust_company_info]] 的 `cust_source`。

```ground:enum
enum: cust_source
fields: [cust_company_info.cust_source]
values:
  "MIGRATORY":
    label: "存量迁移企业"
  "PLATFORM_PUSH":
    label: "运营中台推送"
  "PPLATFORM":
    label: "产融自建企业"
```
