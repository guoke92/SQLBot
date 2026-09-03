---
type: concept
title: 统码
page_key: certification_no
domain: ca_cert_fee
status: published
aliases: ["统一社会信用代码", "certificationNo"]
oid: 1

sources: ["db", "code", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "ca_fee_company.certification_no / ca_fee_order.certification_no"
field_targets: ["ca_fee_company.certification_no", "ca_fee_order.certification_no"]
adjudication: synonym
also_confused_with: []
boundary: "18位统一社会信用代码，企业收费维度唯一"
scope:
  databases: [lowcode_pplatform]
---

# 统码

业务定位：统一社会信用代码（简称统码）是企业收费维度的唯一标识，贯穿企业台账和订单。

## 需求背景

统码作为企业法人身份标识，在 CA 收费业务中用于关联企业台账与订单，避免企业名称重复导致的混淆。

## 版本演进

统码为 18 位，未来可能兼容其他证件类型，但当前仅支持统一社会信用代码。

[[ca_fee_company]] · [[ca_fee_order]] · [[certification_no_unified]]