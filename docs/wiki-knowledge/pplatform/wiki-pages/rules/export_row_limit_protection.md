---
type: rule
title: 导出数据上限保护
page_key: export_row_limit_protection
domain: 资金方规则与异常解决
status: published
aliases:
  - 导出行数上限
oid: 1

sources:
  - code:ExceptionResolutionApplication.exportRecords
  - code:FundRuleInfoApplication.exportRecords
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

该规则约束异常解析和资方规则的导出行为。导出时累计行数超过 50000 行则抛出 BaseException，提示缩小查询范围。分页大小为 500。

## 需求背景

大数据量导出可能导致 OOM 和超时。该规则通过硬性上限保护系统稳定性。

## 版本演进

本规则当前为 v0.1 初始契约版本，尚未记录任何未证实的主张。

```ground:rule
name: "导出数据上限保护"
content: "导出异常解析或资方规则时，累计行数超过 50000 行则抛出 BaseException，提示缩小查询范围。分页大小为 500。"
impact: "防止 OOM 和超时。"
field_targets: []
evidence: "code:ExceptionResolutionApplication.exportRecords / FundRuleInfoApplication.exportRecords"
```