---
type: process
title: 迁移用户首登
page_key: migratory_user_login_flow
domain: 租户迁移
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: processes
field_targets:
  - migratory_user_record.is_login
---

迁入写 N，首登弹窗后写 Y。

```ground:process
name: 迁移用户首登
field: migratory_user_record.is_login
states:
  - value: N
    label: N
    source: code_enum
  - value: Y
    label: Y
    source: code_enum
transitions:
  - from: N
    event: 迁移用户首登
    to: Y
    evidence: "code_path:CustMigratoryService.java:26"
```
