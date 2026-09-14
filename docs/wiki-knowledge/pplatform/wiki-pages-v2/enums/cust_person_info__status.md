---
type: enum
title: status
page_key: cust_person_info__status
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











# status

（权威枚举页：4 值，绑定方式 setter-evidence，主承载 cust_person_info.status；db 实测分布，基线外 1 值。）

```ground:enum
enum: cust_person_info__status
fields: [cust_person_info.status, cust_role_info.status]
values:
  "ADD":
    label: "未激活"
  "EFFECT":
    label: "已激活"
  "WRITEOFF":
    label: "注销"
  "FREEZE":
    label: "冻结"
  "N":
    label: "N"
    note: "db 分布存在但代码枚举未声明（REVIEW）"
```
