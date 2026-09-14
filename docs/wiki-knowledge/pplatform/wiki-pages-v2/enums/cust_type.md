---
type: enum
title: cust_type
page_key: cust_type
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



# cust_type

（权威枚举页：4 值，绑定方式 exact-name，主承载 ca_certification_info.cust_type；db 实测分布，基线外 1 值。）

```ground:enum
enum: cust_type
fields: [cust_change_cfg.cust_type, cust_change_record.cust_type, cust_group_rel.cust_type]
values:
  "1":
    label: "个人客户"
    java_name: "INDIVIDUALS"
  "2":
    label: "企业客户"
    java_name: "ENTERPRISE"
  "3":
    label: "运营方企业客户"
    java_name: "OP_ENTERPRISE"
  "4":
    label: "企业客户"
    java_name: "ENTERPRISEALL"
  "COMPANY":
    label: "COMPANY"
    note: "db 分布存在但代码枚举未声明（REVIEW）"
```
