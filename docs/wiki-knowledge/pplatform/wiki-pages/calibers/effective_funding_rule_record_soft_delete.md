---
type: caliber
title: 有效资方规则记录（软删除）
page_key: effective_funding_rule_record_soft_delete
domain: 资金方规则与异常解决
status: published
aliases:
  - 有效规则记录
oid: 1

sources:
  - code:FundRuleInfoApplication.exportRecords
contract_version: "0.1"
field_targets: [funding_rule_info.enable]
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

该口径定义了 [[funding_rule_info]] 中有效记录（未被软删除）的判定标准：enable 必须等于 'Y'。该口径应用于导出资方规则场景，与 [[effective_exception_resolution]] 类似，都是软删除标志的过滤口径。

## 需求背景

资方规则支持软删除，导出时必须过滤掉 enable != 'Y' 的记录，避免无效数据被导出。

## 版本演进

本口径当前为 v0.1 初始契约版本，尚未记录任何未证实的主张。

```ground:caliber
name: "有效资方规则记录（软删除）"
predicate: "funding_rule_info.enable = 'Y'"
scope: "导出资方规则"
evidence: "code:FundRuleInfoApplication.exportRecords"
```