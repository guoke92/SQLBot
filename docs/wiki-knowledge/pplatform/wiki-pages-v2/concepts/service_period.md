---
type: concept
title: 服务期
page_key: service_period
domain: CA证书收费
status: draft
aliases:
  - 服务周期
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
contract_version: "0.1"
maps_to: ca_fee_company.service_end
field_targets:
  - ca_fee_company.service_end
  - ca_fee_company.service_start
  - ca_fee_order.service_start
  - ca_fee_order.service_end
adjudication: boundary
boundary: 企业主数据保存当前服务期；订单表保存该订单对应的服务期快照
also_confused_with:
  - ca_fee_order.service_end
belong: concepts
field_targets: [ca_fee_company.service_end]
---

「服务期」由起止两个字段表达（`service_start`／`service_end`）。主映射取企业主数据 [[ca_fee_company]] 的当前服务期截止日，订单 [[ca_fee_order]] 上保存的是该笔订单对应的服务期**快照**。

**边界（易混淆）**：企业主数据随续费滚动为最新一期；订单快照永久保留当时周期。续费提醒（剩余 ≤7 天）、到期刷新（`service_end < today`）与「服务期内已缴费」判定都以企业主数据的当前服务期为准，见 [[renewal_remind_expire]]、[[already_paid_in_service]]；白名单豁免还会使用零元豁免特殊值作为服务期截止。

## 需求背景

需要同时满足「当前有效服务期可查询」与「历史订单可追溯」，因此采用「企业存当前 + 订单存快照」的双写结构。

## 版本演进

- v0（本页）：建立术语桥与边界。