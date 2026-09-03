---
type: concept
title: 统码
page_key: unified_social_credit_code
domain: CA证书收费与订单
status: published
aliases: ["统一社会信用代码", "certificationNo"]
oid: 1

sources: ["db", "code", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "ca_fee_company.certification_no"
field_targets: []
adjudication: synonym
also_confused_with: []
scope:
  databases: [lowcode_pplatform]
---

“统码”即统一社会信用代码，是企业唯一标识，在企业台账与订单中用于关联同一企业。其边界为等于 ca_fee_order.certification_no。

## 需求背景

企业维度和订单维度需要通过统码关联，确保订单属于正确的企业，并支持企业维度的缴费状态判断。

## 版本演进

v0.1 草稿：作为术语桥接建立，后续可补充实名/统一社会信用代码校验规则。

相关：[[ca_fee_company]]、[[ca_fee_order]]