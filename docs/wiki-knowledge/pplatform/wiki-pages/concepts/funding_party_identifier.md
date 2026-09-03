---
type: concept
title: 对接方标识
page_key: funding_party_identifier
domain: 资金方规则与异常解决
status: published
aliases:
  - fundingPartyCode
  - partnerCode
  - fundingPartyMark
  - fundingPartyId
oid: 1

sources:
  - db:funding_exception_resolution
  - db:funding_rule_info
  - code:ClientQueryFunderCodeService
  - code:ClientQueryFunderMarkService
maps_to: "funding_exception_resolution.funding_party_code / funding_rule_info.funding_party_mark"
field_targets:
  - funding_exception_resolution.funding_party_code
  - funding_rule_info.funding_party_mark
adjudication: "synonym"
also_confused_with:
  - fundingPartyName
  - fundingKey
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

对接方标识是资金方规则与异常解决领域中的核心概念，用于唯一标识一个资金方。在不同表中字段名不同：[[funding_exception_resolution]] 表中为 funding_party_code，[[funding_rule_info]] 表中为 funding_party_mark，但语义均为资方唯一标识。

## 需求背景

系统通过 RPC 调用 ClientQueryFunderCodeService / ClientQueryFunderMarkService 获取合法对接方列表，并在导入异常解析或资方规则时进行存在性校验（参见 [[funding_party_identifier_existence_check]]）。该标识是 [[exception_resolution_unique_key]] 和 [[funding_rule_create_duplicate_check]] 的组成部分。

## 版本演进

边界说明：在不同表中字段名不同，但语义均为资方唯一标识；fundingKey 来自 RPC 返回，与 fundingPartyCode/Mark 对应。当前为 v0.1 初始契约版本，尚未记录任何未证实的主张。