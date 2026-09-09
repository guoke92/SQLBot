---
type: enum
title: cust_scale
page_key: cust_scale
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

# cust_scale

（权威枚举页：4 值，绑定方式 exact-name，主承载 cust_company_info.cust_scale；db 实测分布，基线外 1 值。）

```ground:enum
enum: cust_scale
fields: [cust_company_info.cust_scale]
values:
  LARGE:
    label: 大型企业
  MIDDLE:
    label: 中型企业
  SMALL:
    label: 小型企业
  MINIATURE:
    label: 微型企业
  qw:
    label: "qw"
    note: db 分布存在但代码枚举未声明（REVIEW）
```
