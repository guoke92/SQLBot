---
type: process
title: 资方规则状态
page_key: funding_rule_info__rule_status
belong: processes
domain: funding_rule
status: draft
anchors: [funding_rule_info.rule_status]
field_targets: [funding_rule_info.rule_status]
sources: ['code_path:FundRuleInfoApplication.java:445', 'code_path:FundRuleInfoApplication.java:296',
  'code_path:FundRuleInfoApplication.java:310']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [funding_rule_info]
---

# 资方规则状态

新建 PENDING；生效 ACTIVE；失效 INACTIVE。运行时查询只取 ACTIVE。

```ground:process
process: 资方规则状态
field: funding_rule_info.rule_status
entry: POST /fund-web/ruleInfo
stages:
- stage: 新建
  transitions:
  - from: PENDING
    event: saveRuleInfo 新增
    to: PENDING
    evidence: code_path:FundRuleInfoApplication.java:445
- stage: 生效
  transitions:
  - from: PENDING
    event: activeRule
    to: ACTIVE
    evidence: code_path:FundRuleInfoApplication.java:296
- stage: 失效
  transitions:
  - from: ACTIVE
    event: inActiveRule
    to: INACTIVE
    evidence: code_path:FundRuleInfoApplication.java:310
```

## 页面链接

- [[tables/funding_rule_info]]
- [[dicts/funding_rule_info__rule_status]]
