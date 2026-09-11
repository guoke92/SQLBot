---
type: caliber
title: 异常解析-有效数据口径
page_key: calibers/exception_resolution_valid_enable_y
domain: funding
status: draft
aliases:
  - 异常解析有效数据
  - exception enable=Y
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:ExceptionResolutionApplication#exportRecords"
  - "code:FundingPartyExceptionResolutionProviderImpl#doQuery"
  - "db:funding_exception_resolution"
contract_version: "0.1"
---

# 异常解析-有效数据口径

## 业务定位

凡是从 [[tables/funding_exception_resolution]] 取数的出口——运营导出、列表查询、对外 Provider 查询——一律附加 `enable = 'Y'`。这意味着「软删除」的语义在本表完全由 `enable` 承担：一条被置为非 `Y` 的异常解析配置对任何读取方都不存在。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。该口径在三个读取面上表现一致，未发现例外路径。

```ground:caliber
caliber: 异常解析-有效数据
predicate: "funding_exception_resolution.enable = 'Y'"
scope: 导出/列表查询/对外Provider查询
evidence: "code:ExceptionResolutionApplication#exportRecords; FundingPartyExceptionResolutionProviderImpl#doQuery"
```

## 关联

- 表：[[tables/funding_exception_resolution]]
- 规则：[[rules/exception_upsert_write]]、[[rules/exception_provider_keyword_contains]]