---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:tenant-setting@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 已生效租户配置有多少
page_key: count-effective-tenant-settings
domain: tenant
anchors:
- tenant_setting_config
---
# 已生效租户配置有多少

问法：已生效租户配置有多少

```ground:pattern
pattern: count-effective-tenant-settings
question: 已生效租户配置有多少
sql: "SELECT COUNT(1) AS effective_tenant_setting_count\nFROM tenant_setting_config\n\
  WHERE status = 'Y'\n  AND enable = 'Y'\n"
verification: PENDING_VALIDATION
```

## 关联
- [[tenant_setting_config]]
