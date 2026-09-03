---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:funding-rule@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 生效中的资金规则有多少
page_key: count-active-funding-rules
domain: funding
anchors:
- funding_rule_info
---
# 生效中的资金规则有多少

问法：生效中的资金规则有多少

```ground:pattern
pattern: count-active-funding-rules
question: 生效中的资金规则有多少
sql: SELECT COUNT(DISTINCT id) AS active_rule_count FROM funding_rule_info WHERE rule_status
  = 'ACTIVE' AND enable = 'Y'
verification: PENDING_VALIDATION
```

## 关联
- [[funding_rule_info]]
