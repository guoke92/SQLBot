---
type: scenario
title: 配置资方规则
page_key: funding_rule_config
belong: scenarios
domain: funding_rule
status: draft
aliases: [资金方规则, 资方准入规则]
sources: ['code_path:l1_intermediate']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [funding_rule_info, funding_rule_detail, funding_rule_front_cfg]
---

# 配置资方规则

规则头按产品+资金方。明细按 rule_info_id。运行时只读 ACTIVE。

```ground:scenario
scenario: funding_rule_config
hubs:
- table: funding_rule_info
  role: master
shared:
- table: funding_rule_detail
  role: detail
- table: funding_rule_front_cfg
  role: front
lifecycle:
- dict: funding_rule_info__rule_status
  process: funding_rule_info__rule_status
```

## 页面链接

- [[tables/funding_rule_detail]]
- [[tables/funding_rule_front_cfg]]
- [[tables/funding_rule_info]]
- [[dicts/funding_rule_info__rule_status]]
- [[processes/funding_rule_info__rule_status]]
