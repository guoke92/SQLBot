---
type: concept
title: 资金方 / 资方（fundingParty）
page_key: concepts/funding_party
domain: funding
status: draft
aliases:
  - fundingParty
  - 资方
  - 对接方
  - 资金方
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:ClientQueryFunderCodeService"
  - "code:ClientQueryFunderMarkService"
contract_version: "0.1"
maps_to: "资方RPC（ClientQueryFunderCodeService / ClientQueryFunderMarkService）返回的 fundingKey + fundingPartyName"
field_targets:
  - funding_exception_resolution.funding_party_name
  - funding_rule_info.funding_party_name
adjudication: synonym
also_confused_with:
  - 金融机构
  - 产品
boundary: "资金方=资方=对接方，均指某产品下对接的金融/资金机构；仅在字段命名（code/mark）上区分，业务含义一致"
---

# 资金方 / 资方（fundingParty）

## 业务定位

在业务口径上，「资金方」「资方」「对接方」是**同义词**，都指某个产品下对接的金融/资金机构；差异只体现在落字段时的命名（`code` 还是 `mark`），业务含义完全一致。资方信息的来源是资方 RPC（`ClientQueryFunderCodeService` / `ClientQueryFunderMarkService`），返回 `fundingKey`（唯一键）与 `fundingPartyName`（名称）两个值。

资方与「金融机构」不是同一层级概念：资金方是**产品视角**下的合作机构配置，而产品本身（`product_code`，如 `ACFLOW` / `RVSFACTOR_PC`）是更上层的分类维度。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。

## 关联

- 概念：[[concepts/funding_key]]、[[concepts/funding_party_code]]、[[concepts/product_code]]