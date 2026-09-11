---
type: concept
title: fundingKey（资方唯一键）
page_key: concepts/funding_key
domain: funding
status: draft
aliases:
  - fundingKey
  - fundingPartyCode
  - fundingPartyMark
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:CustFundingPartyResultDto"
contract_version: "0.1"
maps_to: "CustFundingPartyResultDto.fundingKey（资方唯一键）"
field_targets:
  - funding_exception_resolution.funding_party_code
  - funding_rule_info.funding_party_mark
adjudication: synonym
also_confused_with:
  - fundingPartyName
boundary: "同一资方键：异常解析场景作为 funding_party_code 使用（需先经名称-键组合映射），规则场景作为 funding_party_mark 直接使用；不可与 fundingPartyName 混淆"
---

# fundingKey（资方唯一键）

## 业务定位

`fundingKey` 是 `CustFundingPartyResultDto` 中资方的唯一键，是整个「资金规则与异常处理」主题下**跨表引用资方的唯一锚点**。它有两个使用场景：

| 场景 | 落库字段 | 进入方式 |
| --- | --- | --- |
| 异常解析 | `funding_exception_resolution.funding_party_code` | 需先经「名称-键」组合串映射 |
| 资方规则 | `funding_rule_info.funding_party_mark` | 直接使用 |

**绝不可与 `fundingPartyName` 混淆**：前者是键，后者是展示名。异常解析导出时用 `funding_party_code` 反查映射为「名称(code)」，正是键→名的单向派生。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。

## 关联

- 概念：[[concepts/funding_party_code]]、[[concepts/funding_party]]
- 规则：[[rules/exception_export_funding_party_name_acflow]]