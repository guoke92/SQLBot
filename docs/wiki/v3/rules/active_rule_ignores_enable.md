---
type: rule
title: 运行时生效规则不看 enable
page_key: active_rule_ignores_enable
belong: rules
domain: funding_rule
status: draft
field_targets: [funding_rule_info.rule_status, funding_rule_info.enable]
sources: ['code_path:FundingPartyRuleProviderImpl.java:95']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [funding_rule_info]
---

# 运行时生效规则不看 enable

FundingPartyRuleProviderImpl 按 rule_status=ACTIVE 取规则，未过滤 enable。问生效规则不要再 AND enable=Y。

```ground:rule
rule: 运行时生效规则不看 enable
field_targets: [funding_rule_info.rule_status, funding_rule_info.enable]
impact: query_constraint
content: FundingPartyRuleProviderImpl 按 rule_status=ACTIVE 取规则，未过滤 enable。问生效规则不要再
  AND enable=Y。
evidence: code_path:FundingPartyRuleProviderImpl.java:95
```

## 页面链接

- [[tables/funding_rule_info]]
- [[dicts/funding_rule_info__enable]]
- [[dicts/funding_rule_info__rule_status]]
- [[processes/funding_rule_info__rule_status]]
