---
type: caliber
title: 未成功迁移推数
page_key: failed_migration
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
  - tenant_migarory_log.status
---

未成功或待重试。出向重推还要 direction=OUT。

```ground:caliber
name: 未成功迁移推数
predicate: "tenant_migarory_log.status = 'N'"
scope: tenant_migarory_log
evidence: code
```
