---
type: enum
title: cust_build_type
page_key: cust_build_type
belong: enums
domain: 基线
status: draft
aliases: []
oid: 1
sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# cust_build_type

（权威枚举页：2 值，绑定方式 setter-evidence，主承载 cust_company_info.cust_build_type；db 实测分布，基线外 1 值。）

```ground:enum
enum: cust_build_type
fields: [cust_company_info.cust_build_type]
values:
  PC_BUILD:
    label: 客户录入
  AGW_BUILD:
    label: 平台录入
  SIMPLE:
    label: "SIMPLE"
    note: db 分布存在但代码枚举未声明（REVIEW）
```
