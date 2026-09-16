---
type: caliber
title: 实名已通过联系人
page_key: realname_passed_person
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
  - cust_person_info.real_name_result
---

综合实名成功，不是单看 face_status。

```ground:caliber
name: 实名已通过联系人
predicate: "cust_person_info.real_name_result = 'VERIFIED_SUCCESS'"
scope: cust_person_info
evidence: code
```
