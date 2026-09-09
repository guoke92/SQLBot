---
type: enum
title: status
page_key: cust_role_info__status
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

# status

（权威枚举页：4 值，绑定方式 setter-evidence，主承载 cust_role_info.status；db 实测分布。）

```ground:enum
enum: cust_role_info__status
fields: [cust_role_info.status, cust_person_info.status]
values:
  ADD:
    label: 未激活
  EFFECT:
    label: 已激活
  WRITEOFF:
    label: 注销
  FREEZE:
    label: 冻结
```
