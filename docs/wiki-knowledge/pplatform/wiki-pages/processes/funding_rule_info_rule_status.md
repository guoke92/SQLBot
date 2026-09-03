---
type: process
title: funding_rule_info.rule_status 状态机
page_key: funding_rule_info_rule_status
domain: 资金方规则与异常解决
status: published
aliases:
  - 规则状态机
oid: 1

sources:
  - code:FundRuleInfoApplication
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

该状态机描述 [[funding_rule_info]] 表中 rule_status 字段的生命周期。规则状态包括 PENDING（待生效）、ACTIVE（生效）、INACTIVE（失效），由增强方法 activeRule 和 inActiveRule 驱动状态迁移。

## 需求背景

规则从创建到失效需要明确的业务状态流转。ACTIVE 状态是对外查询的 [[effective_funding_rule]] 口径的基础。版本更新和状态迁移共同维护规则的生命周期。

## 版本演进

本状态机当前为 v0.1 初始契约版本，尚未记录任何未证实的主张。

```ground:state_machine
name: funding_rule_info.rule_status
field: funding_rule_info.rule_status
states:
  - value: PENDING
    label: "待生效"
    source: "code_enum"
  - value: ACTIVE
    label: "生效"
    source: "code_enum"
  - value: INACTIVE
    label: "失效"
    source: "code_enum"
transitions:
  - from: PENDING
    event: activeRule
    to: ACTIVE
    evidence: "code_path:FundRuleInfoApplication.java:activeRule"
  - from: ACTIVE
    event: inActiveRule
    to: INACTIVE
    evidence: "code_path:FundRuleInfoApplication.java:inActiveRule"
  - from: INACTIVE
    event: activeRule
    to: ACTIVE
    evidence: "code_path:FundRuleInfoApplication.java:activeRule"
  - from: PENDING
    event: inActiveRule
    to: INACTIVE
    evidence: "code_path:FundRuleInfoApplication.java:inActiveRule"
  - from: ACTIVE
    event: activeRule
    to: ACTIVE
    evidence: "code_path:FundRuleInfoApplication.java:activeRule"
  - from: INACTIVE
    event: inActiveRule
    to: INACTIVE
    evidence: "code_path:FundRuleInfoApplication.java:inActiveRule"
```