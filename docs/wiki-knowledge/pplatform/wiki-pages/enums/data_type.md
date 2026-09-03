---
type: enum
title: data_type
page_key: data_type
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

# data_type

（权威枚举页：3 值，绑定方式 setter-evidence，主承载 cust_company_info.data_type；db 实测分布。）

```ground:enum
enum: data_type
fields: [cust_company_info.data_type]
values:
  1:
    label: 主数据
  0:
    label: 流程数据
  2:
    label: 编辑过程
```
