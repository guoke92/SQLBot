---
type: rule
title: 异常解析对外查询-关键字包含匹配
page_key: rules/exception_provider_keyword_contains
domain: funding
status: draft
aliases:
  - 报错关键字包含匹配
  - errorMessage.contains
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundingPartyExceptionResolutionProviderImpl#doQuery"
contract_version: "0.1"
---

# 异常解析对外查询-关键字包含匹配

## 业务定位

对外查询先按 `fundingPartyCode + productCode + enable='Y'` 把候选配置全部拉回，再在**内存中**用 `errorMessage.contains(error_keyword)` 过滤，可命中多条并全部返回。因此 `error_keyword` 不是等值键而是**匹配模式**：一条配置的关键字可以是另一条的父串，两条都可能被命中，调用方需按返回顺序自行取舍。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。DB 中的三元组唯一约束（见 [[calibers/exception_resolution_unique_config]]）保证了「同一资方同一产品下关键字不重复」，但**不保证关键字之间不互为子串**。

```ground:rule
rule: 异常解析对外查询-关键字包含匹配
content: "按 fundingPartyCode + productCode + enable='Y' 拉取后，内存过滤 errorMessage.contains(error_keyword)，可命中多条全部返回"
impact: "对外按报错信息匹配异常解析"
field_targets:
  - funding_exception_resolution.error_keyword
  - funding_exception_resolution.enable
evidence: "code:FundingPartyExceptionResolutionProviderImpl#doQuery"
```

## 关联

- 表：[[tables/funding_exception_resolution]]
- 口径：[[calibers/exception_resolution_valid_enable_y]]
- 规则：[[rules/exception_provider_exception_fallback]]