---
type: enum
title: type
page_key: cust_project_code_record__type
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




# type

（权威枚举页：4 值，绑定方式 db-profile，主承载 cust_project_code_record.type；db 实测分布。）

```ground:enum
enum: cust_project_code_record__type
fields: [cust_project_code_record.type]
values:
  "PC_BUILD":
    label: "PC_BUILD"
  "userCompanyRegister":
    label: "userCompanyRegister"
  "产品中心":
    label: "产品中心"
  "产品中心-企业认证成功":
    label: "产品中心-企业认证成功"
```
