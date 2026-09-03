---
type: enum
title: cust_type
page_key: cust_type
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

# cust_type

（权威枚举页：4 值，绑定方式 exact-name，主承载 ca_certification_info.cust_type；db 实测分布，基线外 1 值。）

```ground:enum
enum: cust_type
fields: [ca_certification_info.cust_type, cust_change_cfg.cust_type, cust_change_record.cust_type, cust_group_rel.cust_type]
values:
  1:
    label: 个人客户
  2:
    label: 企业客户
  3:
    label: 运营方企业客户
  4:
    label: 企业客户
  COMPANY:
    label: "COMPANY"
    note: db 分布存在但代码枚举未声明（REVIEW）
```
