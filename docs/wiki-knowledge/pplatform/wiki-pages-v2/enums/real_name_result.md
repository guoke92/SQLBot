---
type: enum
title: real_name_result
page_key: real_name_result
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












# real_name_result

（权威枚举页：3 值，绑定方式 setter-evidence，主承载 cust_person_info.real_name_result；db 实测分布。）

```ground:enum
enum: real_name_result
fields: [cust_person_info.real_name_result]
values:
  "INIT":
    label: "未认证"
  "VERIFIED_SUCCESS":
    label: "认证成功"
  "VERIFIED_FAILED":
    label: "认证失败"
```
