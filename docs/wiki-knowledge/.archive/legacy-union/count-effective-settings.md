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
page_key: count-effective-settings
domain: tenant
anchors:
- tenant_setting_config
---
# 已生效租户配置有多少

问法：已生效租户配置有多少

```ground:pattern
pattern: count-effective-settings
question: 已生效租户配置有多少
sql: 'SELECT COUNT(DISTINCT id) AS effective_tenant_setting_count FROM tenant_setting_config
  WHERE status = ''Y'' AND enable = ''Y''

  '
verification: PENDING_VALIDATION
```

## 关联
- [[tenant_setting_config]]
