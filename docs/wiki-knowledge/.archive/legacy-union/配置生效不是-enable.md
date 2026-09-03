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
type: rule
title: 配置生效不是 enable
page_key: 配置生效不是-enable
domain: tenant
field_targets:
- tenant_setting_config.status
- tenant_setting_config.enable
---
# 配置生效不是 enable

enable 是行是否可用；是否已生效看 status。

```ground:rule
rule: setting-status-not-enable
field_targets:
- tenant_setting_config.status
- tenant_setting_config.enable
impact: query_constraint
content: enable 是行是否可用；是否已生效看 status。
scope: 已生效租户、待生效租户
```

## 关联
- [[tenant_setting_config]]
