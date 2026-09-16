---
type: process
title: 迁移日志成功标记
page_key: migratory_log_status_flow
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
  - tenant_migarory_log.status
---

默认 N，出向成功回写 Y。Y/N 来自 BooleanEnum，中文不另编。

```ground:process
name: 迁移日志成功标记
field: tenant_migarory_log.status
states:
  - value: N
    label: N
    source: code_enum
  - value: Y
    label: Y
    source: code_enum
transitions:
  - from: N
    event: 出向推数成功回写
    to: Y
    evidence: "code_path:TenantMigaroryLogDaoImpl.java:87"
```
