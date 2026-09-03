---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:funding-party-rules@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 某资方某产品的生效校验规则
page_key: active-rule-by-party
domain: 资金方规则
anchors:
- funding_rule_detail
- funding_rule_info
---
# 某资方某产品的生效校验规则

问法：某资方某产品的生效校验规则

```ground:pattern
pattern: active-rule-by-party
question: 某资方某产品的生效校验规则
sql: "SELECT d.rule_key, d.rule_value, d.rule_layer FROM funding_rule_detail d JOIN\
  \ funding_rule_info i ON i.id = d.rule_info_id WHERE i.funding_party_mark = ? AND\
  \ i.product_code = ?\n  AND i.rule_status = 'ACTIVE' AND i.enable = 'Y' AND d.enable\
  \ = 'Y'"
verification: PENDING_VALIDATION
```

## 关联
- [[funding_rule_detail]]
- [[funding_rule_info]]
