---
type: enum
title: user_type
page_key: user_type
belong: enums
domain: 基线
status: published
aliases: [管理员, 企业管理员, 经办人, 游客]
oid: 1
sources: ["db:cust_person_info", "db:db-profile.yaml"]
created: '2026-09-10'
updated: '2026-09-10'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# user_type

（权威枚举页：3 值，主承载 cust_person_info.user_type。）

```ground:enum
enum: user_type
fields: [cust_person_info.user_type]
values:
  accountAdmin:
    label: 管理员
  accountNormal:
    label: 经办人
  accountGuest:
    label: 游客
```

相关：[[cust_person_info]] [[admin]] [[operator]]
