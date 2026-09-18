---
type: caliber
title: 生效中的资方规则
page_key: active_funding_rule
belong: calibers
domain: funding_rule
status: draft
field_targets: [funding_rule_info.rule_status]
sources: ['code_path:FundingPartyRuleProviderImpl.java:95']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [funding_rule_info, funding_rule_detail]
---

# 生效中的资方规则

运行时按资金方标识+产品编码取 ACTIVE。列表查询未过滤 enable。不要用 PENDING/INACTIVE 当生效规则。

```ground:caliber
caliber: 生效中的资方规则
field_targets: [funding_rule_info.rule_status]
predicate: funding_rule_info.rule_status = 'ACTIVE'
scope: global
boundary: 运行时按资金方标识+产品编码取 ACTIVE。列表查询未过滤 enable。不要用 PENDING/INACTIVE 当生效规则。
using_relations:
- left: funding_rule_info.id
  right: funding_rule_detail.rule_info_id
evidence: code_path:FundingPartyRuleProviderImpl.java:95
```

## 页面链接

- [[tables/funding_rule_detail]]
- [[tables/funding_rule_info]]
- [[dicts/funding_rule_info__rule_status]]
- [[processes/funding_rule_info__rule_status]]
