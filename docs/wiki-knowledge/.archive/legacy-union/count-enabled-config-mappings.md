---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:customer-config@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 启用的渠道映射有多少
page_key: count-enabled-config-mappings
domain: config
anchors:
- cust_config_mapping
---
# 启用的渠道映射有多少

问法：启用的渠道映射有多少

```ground:pattern
pattern: count-enabled-config-mappings
question: 启用的渠道映射有多少
sql: 'SELECT COUNT(1) AS enabled_mapping_count

  FROM cust_config_mapping

  WHERE enable = ''Y''

  '
verification: PENDING_VALIDATION
```

## 关联
- [[cust_config_mapping]]
