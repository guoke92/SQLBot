---
type: rule
title: 资方规则详情保存-幂等更新
page_key: rules/rule_detail_save_idempotent
domain: funding
status: draft
aliases:
  - 明细幂等落库
  - ruleKey 幂等更新
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundRuleInfoApplication#saveRuleInfo"
contract_version: "0.1"
---

# 资方规则详情保存-幂等更新

## 业务定位

明细保存以 `ruleInfoId + ruleKey + enable='Y'` 为幂等键：命中即更新，未命中即新增。**关键细节**：不在 `ruleMap` 中出现的 `frontKey` 直接跳过，不中断保存——即「本次没提交的字段」保持原样，而不是被置空或删除。这让前端可以只提交变更字段。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。与主表版本累加（[[rules/rule_info_update_version_increment]]）配合：每次保存主表 version+1，明细带新版本写入。

```ground:rule
rule: 资方规则详情保存-幂等更新
content: "按 ruleInfoId + ruleKey + enable='Y' 命中则更新，否则新增；ruleMap 中不存在的 frontKey 跳过（不中断）"
impact: "明细按 key 幂等落库"
field_targets:
  - funding_rule_detail.rule_key
  - funding_rule_detail.rule_value
  - funding_rule_detail.enable
evidence: "code:FundRuleInfoApplication#saveRuleInfo"
```

## 关联

- 表：[[tables/funding_rule_detail]]
- 概念：[[concepts/rule_key]]
- 口径：[[calibers/funding_rule_detail_valid_enable_y]]