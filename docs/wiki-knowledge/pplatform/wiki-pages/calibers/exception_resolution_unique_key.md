---
type: caliber
title: 异常解析唯一键
page_key: exception_resolution_unique_key
domain: 资金方规则与异常解决
status: published
aliases:
  - 异常解析唯一性
oid: 1

sources:
  - db_index:funding_exception_resolution_un
  - code:ExceptionResolutionApplication.collectFundingPartyCodeErrors
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

该口径定义了 [[funding_exception_resolution]] 中记录的唯一性约束：funding_party_code、error_keyword、product_code 三个字段的组合必须唯一。该约束由数据库唯一索引和导入查重逻辑共同保证。

## 需求背景

同一产品、同一对接方、同一报错关键字只应有一条异常解析配置。导入时的重复检测逻辑（参见 [[exception_resolution_import_duplicate_detection]]）和数据库唯一索引共同维护这一约束。

## 版本演进

本口径当前为 v0.1 初始契约版本，尚未记录任何未证实的主张。

```ground:caliber
name: "异常解析唯一键"
predicate: "funding_exception_resolution.(funding_party_code + error_keyword + product_code) 唯一"
scope: "导入时查重、数据库唯一索引"
evidence: "db_index:funding_exception_resolution_un + code:ExceptionResolutionApplication.collectFundingPartyCodeErrors"
```