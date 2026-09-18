---
type: rule
title: 同一产品下同一资金方只能有一条规则头
page_key: unique_product_funding_party_rule
belong: rules
domain: funding_rule
status: draft
field_targets: [funding_rule_info.product_code, funding_rule_info.funding_party_mark]
sources: ['code_path:FundRuleInfoApplication.java:431']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [funding_rule_info]
---

# 同一产品下同一资金方只能有一条规则头

新增时按 product_code + funding_party_mark 查重，已存在则拒绝。

```ground:rule
rule: 同一产品下同一资金方只能有一条规则头
field_targets: [funding_rule_info.product_code, funding_rule_info.funding_party_mark]
impact: write_constraint
content: 新增时按 product_code + funding_party_mark 查重，已存在则拒绝。
evidence: code_path:FundRuleInfoApplication.java:431
```

## 页面链接

- [[tables/funding_rule_info]]
- [[dicts/funding_rule_info__product_code]]
