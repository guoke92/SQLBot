---
type: process
title: 资方规则状态机
page_key: processes/funding_rule_status_machine
domain: funding
status: draft
aliases:
  - rule_status 状态机
  - 规则状态流转
  - 资方规则生命周期
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundRuleInfoApplication#saveRuleInfo"
  - "code:FundRuleInfoApplication#activeRule"
  - "code:FundRuleInfoApplication#inActiveRule"
  - "code:FundingPartyRuleProviderImpl#doQuery"
contract_version: "0.1"
---

# 资方规则状态机

## 业务定位

资方规则不是一个「保存即生效」的对象，而是带三态的生命周期对象：`PENDING`（待生效）→ `ACTIVE`（已生效）⇄ `INACTIVE`（已失效）。新增入口 `saveRuleInfo` 在 `ruleInfoId` 为空时**强制**落到 `PENDING`，运营必须再调用 `activeRule` 才对外可见；`inActiveRule` 可从 `ACTIVE` 或 `PENDING` 直接落到 `INACTIVE`，但**没有**从 `INACTIVE` 回到 `PENDING` 的路径——`INACTIVE` 只能重新生效为 `ACTIVE`。

外部消费方（Dubbo：[[rules/rule_info_provider_active_only]]）只按 `rule_status='ACTIVE'` 取数，取不到即返回 null，因此「已失效」与「待生效」对外表现一致：都不可见。

## 需求背景

无语义分析挂载的需求文档锚点。状态取值来自代码枚举，迁移路径来自 `saveRuleInfo` / `activeRule` / `inActiveRule` 三个入口方法的证据。

## 版本演进

无 `action=uncovered` 的主张。状态与版本耦合：每次 `saveRuleInfo`（`ruleInfoId` 非空）使 `version` 累加 1（见 [[rules/rule_info_update_version_increment]]），但状态迁移本身不改 `version`，因此同一 `version` 下规则可能经历 `PENDING→ACTIVE→INACTIVE` 的状态变化，版本号并不等于状态轮次。

```ground:process
process: 资方规则状态机
field: funding_rule_info.rule_status
states:
  - value: PENDING
    label: 待生效
    source: code_enum
  - value: ACTIVE
    label: 已生效
    source: code_enum
  - value: INACTIVE
    label: 已失效
    source: code_enum
transitions:
  - from: "(无)"
    event: saveRuleInfo 新增（ruleInfoId 为空）
    to: PENDING
    evidence: "code_path:FundRuleInfoApplication.java#saveRuleInfo"
  - from: PENDING
    event: activeRule 生效
    to: ACTIVE
    evidence: "code_path:FundRuleInfoApplication.java#activeRule"
  - from: INACTIVE
    event: activeRule 生效
    to: ACTIVE
    evidence: "code_path:FundRuleInfoApplication.java#activeRule"
  - from: ACTIVE
    event: inActiveRule 失效
    to: INACTIVE
    evidence: "code_path:FundRuleInfoApplication.java#inActiveRule"
  - from: PENDING
    event: inActiveRule 失效
    to: INACTIVE
    evidence: "code_path:FundRuleInfoApplication.java#inActiveRule"
```

## 关联

- 表：[[tables/funding_rule_info]]
- 口径：[[calibers/funding_rule_info_active_rule]]、[[calibers/funding_rule_info_valid_enable_y]]
- 规则：[[rules/rule_info_create_initial_pending]]、[[rules/rule_info_provider_active_only]]、[[rules/rule_info_update_version_increment]]