---
type: enum
title: real_name_result
page_key: real_name_result
domain: 经办人/联系人/管理员管理
status: draft
aliases: [实名认证成功]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# real_name_result

`RealNameResultEnum`：任一项通过→认证成功；两项皆空/待核查/库无记录→未认证；否则失败。

```ground:enum
enum: real_name_result
fields:
  - cust_person_info.real_name_result
values:
  "INIT":
    label: "未认证"
  "VERIFIED_SUCCESS":
    label: "认证成功"
  "VERIFIED_FAILED":
    label: "认证失败"
```
