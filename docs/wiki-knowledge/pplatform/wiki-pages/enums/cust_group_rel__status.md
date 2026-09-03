---
type: enum
title: status
page_key: cust_group_rel__status
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

# status

（权威枚举页：3 值，绑定方式 setter-evidence，主承载 cust_group_rel.status；db 实测分布。）

```ground:enum
enum: cust_group_rel__status
fields: [cust_group_rel.status]
values:
  INEFFECTIVE:
    label: 未生效
  EFFECTIVE:
    label: 已生效
  REJECTED:
    label: 已拒绝
```
