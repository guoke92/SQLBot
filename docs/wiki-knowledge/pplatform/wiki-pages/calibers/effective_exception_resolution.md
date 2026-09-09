---
type: caliber
title: 有效异常解析配置
page_key: effective_exception_resolution
belong: calibers
domain: 资金方规则与异常解决
status: published
aliases:
  - 有效异常解析
oid: 1

sources:
  - code:ExceptionResolutionApplication.exportRecords
  - code:FundingPartyExceptionResolutionProviderImpl.doQuery
contract_version: "0.1"
field_targets: [funding_exception_resolution.enable]
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

该口径定义了 [[funding_exception_resolution]] 中有效数据的判定标准：enable 字段必须等于 'Y'。该口径应用于导出和 Dubbo Provider 查询两个场景，确保软删除的异常解析配置不会被暴露给用户。

## 需求背景

异常解析配置需要支持软删除，避免物理删除导致的历史数据丢失。在导出和对外查询时，必须过滤掉 enable != 'Y' 的记录。

## 版本演进

本口径当前为 v0.1 初始契约版本，尚未记录任何未证实的主张。

```ground:caliber
name: "有效异常解析配置"
predicate: "funding_exception_resolution.enable = 'Y'"
scope: "导出、Dubbo Provider 查询"
evidence: "code:ExceptionResolutionApplication.exportRecords / FundingPartyExceptionResolutionProviderImpl.doQuery"
```