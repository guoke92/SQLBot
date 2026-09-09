---
type: rule
title: 对接方标识存在性校验
page_key: funding_party_identifier_existence_check
belong: rules
domain: 资金方规则与异常解决
status: published
aliases:
  - 标识存在性校验
oid: 1

sources:
  - code:ExceptionResolutionApplication.collectFundingPartyCodeErrors
  - code:FundRuleInfoApplication.collectFundingPartyMarkErrors
contract_version: "0.1"
field_targets: [funding_exception_resolution.funding_party_code, funding_rule_info.funding_party_mark]
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

该规则约束导入异常解析或资方规则时的对接方标识校验。必须通过 RPC 调用 ClientQueryFunderCodeService / ClientQueryFunderMarkService 获取合法对接方列表，校验导入行中的标识存在于列表中。

## 需求背景

防止无效资金方标识入库是数据完整性的重要保障。该规则与 [[funding_party_identifier]] 概念直接相关。

## 版本演进

本规则当前为 v0.1 初始契约版本，尚未记录任何未证实的主张。

```ground:rule
name: "对接方标识存在性校验"
content: "导入异常解析或资方规则时，必须通过 RPC 调用 ClientQueryFunderCodeService / ClientQueryFunderMarkService 获取合法对接方列表，校验导入行中的标识存在于列表中。"
impact: "防止无效资金方标识入库。"
field_targets:
  - funding_exception_resolution.funding_party_code
  - funding_rule_info.funding_party_mark
evidence: "code:ExceptionResolutionApplication.collectFundingPartyCodeErrors / FundRuleInfoApplication.collectFundingPartyMarkErrors"
```

相关：[[funding_exception_resolution]] [[funding_rule_info]]
