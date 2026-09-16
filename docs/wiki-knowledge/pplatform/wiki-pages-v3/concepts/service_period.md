---
type: concept
title: 服务期
page_key: service_period
domain: CA证书收费
status: draft
aliases: [服务周期]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:ca_fee_company"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: concepts
maps_to: ca_fee_company.service_end
field_targets:
  - ca_fee_company.service_start
  - ca_fee_company.service_end
adjudication: boundary
boundary: 企业主档保存当前服务期；订单保存该单快照
also_confused_with: [ca_fee_order.service_end]
---

「服务期」由 `service_start` / `service_end` 表达。问「当前还在服务期内吗」落 [[ca_fee_company]] 的当前截止日；[[ca_fee_order]] 上的同名列是该笔订单快照，续费后主档滚动、订单不改。

续费提醒与到期回落都以企业当前服务期为准，见 [[renew_remind_rule]]。不要把订单 `service_end` 当 JOIN 键。
