---
type: caliber
title: 未激活联系人
page_key: pending_person
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
  - cust_person_info.status
---

账号未激活。不是建档 `cust_build_status`。

```ground:caliber
name: 未激活联系人
predicate: "cust_person_info.status = 'ADD'"
scope: cust_person_info
evidence: code
```
