---
type: rule
title: 重推只作出向迁移日志
page_key: push_by_log_out_only
domain: 租户迁移
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: rules
field_targets:
  - tenant_migarory_log.direction
  - tenant_migarory_log.type
---

pushByLog 只处理 direction=OUT，且 type 不是校验类 *_SYNC_VALIDATE。

```ground:rule
name: 重推只作出向迁移日志
content: pushByLog 只处理 direction=OUT，且 type 不是校验类 *_SYNC_VALIDATE。
field_targets: [tenant_migarory_log.direction, tenant_migarory_log.type]
evidence: "code_path:MigratoryPointServiceImpl.java:318"
```
