---
type: rule
title: 规则明细更新策略
page_key: rule_detail_update_strategy
domain: 资金方规则与异常解决
status: published
aliases:
  - 明细更新
oid: 1

sources:
  - code:FundRuleInfoApplication.saveRuleInfo
contract_version: "0.1"
field_targets: [funding_rule_detail.enable, funding_rule_detail.rule_key, funding_rule_detail.version]
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

该规则约束 [[funding_rule_detail]] 表的保存行为。保存规则详情时，对每个 frontKey 先查询是否存在 enable='Y' 的 detail 记录；若存在则复用该记录并更新字段，若不存在则新建。不会物理删除旧版本明细。

## 需求背景

同一 ruleInfoId + ruleKey 下需要保持只有一条 enable='Y' 记录，以支持规则版本更新和软删除。

## 版本演进

本规则当前为 v0.1 初始契约版本，尚未记录任何未证实的主张。

```ground:rule
name: "规则明细更新策略"
content: "保存规则详情时，对每个 frontKey 先查询是否存在 enable='Y' 的 detail 记录；若存在则复用该记录并更新字段，若不存在则新建。不会物理删除旧版本明细。"
impact: "同一 ruleInfoId + ruleKey 下只有一条 enable='Y' 记录，旧值被覆盖，版本号更新。"
field_targets:
  - funding_rule_detail.rule_key
  - funding_rule_detail.enable
  - funding_rule_detail.version
evidence: "code:FundRuleInfoApplication.saveRuleInfo 公共明细保存循环"
```