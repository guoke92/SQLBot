---
type: caliber
title: 迁移用户未首登
page_key: pending_migratory_login
domain: 租户迁移
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
  - migratory_user_record.is_login
---

存量迁移用户尚未首登。

```ground:caliber
name: 迁移用户未首登
predicate: "migratory_user_record.is_login = 'N'"
scope: migratory_user_record
evidence: code
```
