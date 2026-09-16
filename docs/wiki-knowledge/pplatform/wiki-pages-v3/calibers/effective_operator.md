---
type: caliber
title: 有效经办人
page_key: effective_operator
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
---

已激活且启用的经办人。

```ground:caliber
name: 有效经办人
predicate: "cust_person_info.user_type = 'accountNormal' AND cust_person_info.status = 'EFFECT' AND cust_person_info.enable = 'Y'"
scope: cust_person_info
evidence: code
```
