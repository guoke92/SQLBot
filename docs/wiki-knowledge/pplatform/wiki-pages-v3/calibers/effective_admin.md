---
type: caliber
title: 有效管理员
page_key: effective_admin
domain: 经办人/联系人/管理员管理
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: calibers
field_targets:
  - cust_person_info.user_type
  - cust_person_info.status
  - cust_person_info.enable
---

企业下当前有效管理员。同一企业角色通常只有一个；替换时旧管理员进入冻结。

```ground:caliber
name: 有效管理员
predicate: "cust_person_info.user_type = 'accountAdmin' AND cust_person_info.status = 'EFFECT' AND cust_person_info.enable = 'Y'"
scope: cust_person_info
evidence: code
```
