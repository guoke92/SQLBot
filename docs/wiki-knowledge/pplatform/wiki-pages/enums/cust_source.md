---
type: enum
title: cust_source
page_key: cust_source
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

# cust_source

（权威枚举页：3 值，绑定方式 setter-evidence，主承载 cust_company_info.cust_source；db 实测分布，基线外 1 值。）

```ground:enum
enum: cust_source
fields: [cust_company_info.cust_source]
values:
  PLATFORM_PUSH:
    label: 运营中台推送
  MIGRATORY:
    label: 存量迁移企业
  PPLATFORM:
    label: 产融自建企业
  PLATFORM:
    label: "PLATFORM"
    note: db 分布存在但代码枚举未声明（REVIEW）
```
