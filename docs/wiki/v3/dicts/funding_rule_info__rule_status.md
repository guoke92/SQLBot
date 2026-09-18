---
type: dict
title: funding_rule_info.rule_status
page_key: funding_rule_info__rule_status
belong: dicts
status: draft
anchors: [funding_rule_info.rule_status]
sources: ['database_profile:funding_rule_info.rule_status', 'database_schema:funding_rule_info.rule_status',
  'code_path:RuleStatusEnum.java:17', 'code_path:RuleStatusEnum.java:18', 'code_path:RuleStatusEnum.java:19']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [funding_rule_info]
---

# funding_rule_info.rule_status

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `funding_rule_info.rule_status`，表页 [[tables/funding_rule_info]]。

## 取值

```ground:dict
dict: funding_rule_info__rule_status
fields: [funding_rule_info.rule_status]
values:
  PENDING: {trust: confirmed, label: 待生效, evidence: 'code_path:RuleStatusEnum.java:17'}
  ACTIVE: {trust: confirmed, label: 生效中, evidence: 'code_path:RuleStatusEnum.java:18'}
  INACTIVE: {trust: confirmed, label: 已失效, evidence: 'code_path:RuleStatusEnum.java:19'}
triage: keep
```
