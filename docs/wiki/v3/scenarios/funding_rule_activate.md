---
type: scenario
title: 生效资方规则
page_key: funding_rule_activate
belong: scenarios
domain: funding_rule
status: draft
sources: ['code_path:l1_intermediate']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [funding_rule_info]
---

# 生效资方规则

生效资方规则

```ground:scenario
scenario: funding_rule_activate
hubs:
- table: funding_rule_info
  role: master
lifecycle:
- dict: funding_rule_info__rule_status
  process: funding_rule_info__rule_status
```

## 页面链接

- [[tables/funding_rule_info]]
- [[dicts/funding_rule_info__rule_status]]
- [[processes/funding_rule_info__rule_status]]
