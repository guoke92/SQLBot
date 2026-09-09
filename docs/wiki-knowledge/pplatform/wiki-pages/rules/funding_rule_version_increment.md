---
type: rule
title: 资方规则版本递增
page_key: funding_rule_version_increment
belong: rules
domain: 资金方规则与异常解决
status: published
aliases:
  - 版本递增
oid: 1

sources:
  - code:FundRuleInfoApplication.saveRuleInfo
contract_version: "0.1"
field_targets: [funding_rule_detail.version, funding_rule_info.version]
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

该规则约束 [[funding_rule_info]] 和 [[funding_rule_detail]] 的版本更新行为。更新资金方规则时，将 funding_rule_info.version 在原值基础上加 1，并同步更新到新插入或更新的 funding_rule_detail.version。

## 需求背景

规则需要维护版本历史。版本号整数递增，记录每次规则更新。

## 版本演进

本规则当前为 v0.1 初始契约版本，尚未记录任何未证实的主张。

```ground:rule
name: "资方规则版本递增"
content: "更新资金方规则时，将 funding_rule_info.version 在原值基础上加 1，并同步更新到新插入/更新的 funding_rule_detail.version。"
impact: "维护规则版本变化历史。"
field_targets:
  - funding_rule_info.version
  - funding_rule_detail.version
evidence: "code:FundRuleInfoApplication.saveRuleInfo 更新分支"
```