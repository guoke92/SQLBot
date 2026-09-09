---
type: rule
title: 关键字匹配规则
page_key: keyword_matching_rule
belong: rules
domain: 资金方规则与异常解决
status: published
aliases:
  - 错误匹配规则
oid: 1

sources:
  - code:FundingPartyExceptionResolutionProviderImpl.doQuery
contract_version: "0.1"
field_targets: [funding_exception_resolution.error_keyword]
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

该规则约束异常解析查询时的关键字匹配行为。在内存中判断 errorMessage 字符串是否包含 errorKeyword 子串（区分大小写，代码未做忽略大小写处理）。

## 需求背景

该规则直接影响 [[error_keyword]] 的匹配效果。大小写敏感可能导致匹配与预期不一致，是需要注意的约束。

## 版本演进

本规则当前为 v0.1 初始契约版本，尚未记录任何未证实的主张。

```ground:rule
name: "关键字匹配规则"
content: "异常解析查询时，在内存中判断 errorMessage 字符串是否包含 errorKeyword 子串（区分大小写，代码未做忽略大小写处理）。"
impact: "大小写敏感，可能导致匹配与预期不一致。"
field_targets:
  - funding_exception_resolution.error_keyword
evidence: "code:FundingPartyExceptionResolutionProviderImpl.doQuery filter 逻辑"
```

相关：[[funding_exception_resolution]]
