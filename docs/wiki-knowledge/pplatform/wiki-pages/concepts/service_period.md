---
type: concept
title: 服务周期
page_key: service_period
domain: CA证书收费与订单
status: published
aliases: ["服务期"]
oid: 1

sources: ["db", "code", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "ca_fee_company.service_start/service_end"
field_targets: []
adjudication: synonym
also_confused_with: []
scope:
  databases: [lowcode_pplatform]
---

“服务周期”是 CA 服务费的计费服务有效期，由起始日和截止日构成。它用于判断是否服务期内已缴费、是否到期需要续费。

## 需求背景

服务到期处理、规则评估都依赖服务周期的起止日期，必须明确其边界为起始日和截止日。

## 版本演进

v0.1 草稿：作为术语桥接建立，后续可补充时区/含边界等口径细节。

相关：[[ca_fee_company]]、[[ca_fee_order]]、[[service_expiry_processing]]、[[paid_within_service_period]]