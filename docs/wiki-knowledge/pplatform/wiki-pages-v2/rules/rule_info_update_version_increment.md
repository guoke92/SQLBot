---
type: rule
title: 资方规则-更新version+1
page_key: rules/rule_info_update_version_increment
domain: funding
status: draft
aliases:
  - 规则版本累加
  - version+1
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundRuleInfoApplication#saveRuleInfo"
contract_version: "0.1"
---

# 资方规则-更新version+1

## 业务定位

`ruleInfoId` 不为空时视为更新：`version` 在原有基础上累加 1，并回写 `funding_party_name`。明细行随主表写入同一 `version`（见 [[tables/funding_rule_detail]]），因此版本号是「规则内容快照」的标识，可用于追溯某一版规则的具体取值。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。DB 实测明细 `version` 分布为 1/2/3/4/6/8/9/13/17/23/25，说明版本累加是连续的，而明细并非每版都写（跳号来自未落明细的更新）。

```ground:rule
rule: 资方规则-更新version+1
content: "ruleInfoId 不为空时 version 累加 1，并回写 funding_party_name"
impact: "规则版本可追溯，明细携带版本"
field_targets:
  - funding_rule_info.version
  - funding_rule_detail.version
evidence: "code:FundRuleInfoApplication#saveRuleInfo"
```

## 关联

- 表：[[tables/funding_rule_info]]、[[tables/funding_rule_detail]]
- 规则：[[rules/rule_detail_save_idempotent]]