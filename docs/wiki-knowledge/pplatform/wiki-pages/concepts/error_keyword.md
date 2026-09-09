---
type: concept
title: 报错关键字
page_key: error_keyword
belong: concepts
domain: 资金方规则与异常解决
status: published
aliases:
  - errorKeyword
  - errorMessage
oid: 1

sources:
  - db:funding_exception_resolution.error_keyword
  - code:FundingPartyExceptionResolutionProviderImpl
maps_to: "funding_exception_resolution.error_keyword"
field_targets:
  - funding_exception_resolution.error_keyword
adjudication: "synonym"
also_confused_with:
  - errorReason
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

报错关键字是异常解析配置中的匹配依据，存储在 [[funding_exception_resolution]] 表的 error_keyword 字段中。查询时在内存中判断 errorMessage 是否包含 errorKeyword 子串，参见 [[keyword_matching_rule]]。

## 需求背景

资金方对接过程中会产生各种报错信息，系统需要根据报错关键字匹配预先配置的处理方案。该概念与 [[funding_party_identifier]] 和 [[product_code]] 共同构成 [[exception_resolution_unique_key]]。

## 版本演进

边界说明：在查询接口 FundingPartyExceptionQyDto 中入参名为 errorKeyword，但注释常写作 errorMessage；实际匹配逻辑是 errorMessage.contains(errorKeyword)。当前为 v0.1 初始契约版本，尚未记录任何未证实的主张。