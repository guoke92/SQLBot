---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:person-user@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 管理员
page_key: user_type
domain: person
aliases:
- 企业管理员
anchors:
- user_type
---
# 管理员

user_type=accountAdmin 且启用、生效的联系人。

```ground:enum
enum: user_type
fields:
- cust_person_info.user_type
values:
  accountAdmin:
    label: 管理员
  accountNormal:
    label: 经办人
  accountGuest:
    label: 游客
```

## 关联
- [[cust_person_info|cust_person_info]]
