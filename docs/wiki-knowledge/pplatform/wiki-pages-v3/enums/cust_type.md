---
type: enum
title: cust_type
page_key: cust_type
domain: 基线
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CustTypeEnum.java"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# cust_type

[[ca_certification_info]] 的 `cust_type`。

```ground:enum
enum: cust_type
fields: [ca_certification_info.cust_type]
values:
  "1":
    label: "个人客户"
  "2":
    label: "企业客户"
  "3":
    label: "运营方企业客户"
  "4":
    label: "企业客户"
```
