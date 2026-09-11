---
type: rule
title: 异常解析-导出资金方名称映射固定ACFLOW
page_key: rules/exception_export_funding_party_name_acflow
domain: funding
status: draft
aliases:
  - 导出资金方名称映射
  - mapFundingPartyCode ACFLOW
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:ExceptionResolutionApplication#exportRecords"
contract_version: "0.1"
---

# 异常解析-导出资金方名称映射固定ACFLOW

## 业务定位

导出时使用 `mapFundingPartyCode(ProductCodeEnum.ACFLOW)` 把 `funding_party_code` 反查为「名称(code)」写入 `funding_party_name` 列。**映射被硬编码为 ACFLOW 产品**：当导出的记录属于其他产品（如 `RVSFACTOR_PC`）时，映射结果可能为空，导致跨产品导出时资金方名称展示缺失。

这是本主题下最需要关注的实现约束——它把「按产品维度的资方映射」错误地固定到了单一产品。详见 REVIEW 待确认项。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。该行为是否为缺陷、是否已有后续修复，分析中无证据。

```ground:rule
rule: 异常解析-导出资金方名称映射固定ACFLOW
content: "导出时使用 mapFundingPartyCode(ProductCodeEnum.ACFLOW) 将 funding_party_code 映射为「名称(code)」；非 ACFLOW 产品（如 RVSFACTOR_PC）记录映射结果可能为空"
impact: "跨产品导出时资金方名称展示可能缺失"
field_targets:
  - funding_exception_resolution.funding_party_code
  - funding_exception_resolution.funding_party_name
evidence: "code:ExceptionResolutionApplication#exportRecords"
```

## 关联

- 表：[[tables/funding_exception_resolution]]
- 概念：[[concepts/product_code]]、[[concepts/funding_party_code]]、[[concepts/funding_key]]