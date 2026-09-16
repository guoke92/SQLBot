---
type: enum
title: user_type
page_key: user_type
domain: 经办人/联系人/管理员管理
status: draft
aliases: [管理员, 经办人]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# user_type

[[cust_person_info]] 的 `user_type`。`UserTypeEnum` dictKey：accountAdmin 管理员 / accountNormal 经办人 / accountGuest 游客。落库是 dictKey，不是枚举名 admin/operator。

```ground:enum
enum: user_type
fields:
  - cust_person_info.user_type
values:
  "accountAdmin":
    label: "管理员"
  "accountNormal":
    label: "经办人"
  "accountGuest":
    label: "游客"
```
