---
type: concept
title: 缴费订单
page_key: fee_order
domain: CA证书收费
status: draft
aliases:
  - CA服务费订单
  - 订单
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
contract_version: "0.1"
maps_to: ca_fee_order.order_no
field_targets:
  - ca_fee_order.order_no
adjudication: boundary
boundary: 订单维度以 order_no 标识；企业维度以 certification_no 一统码一行
also_confused_with:
  - ca_fee_company.certification_no
belong: concepts
field_targets: [ca_fee_order.order_no]
---

「缴费订单」在数据上以 `ca_fee_order.order_no` 标识，一行代表一次缴费行为；对应的表页是 [[ca_fee_order]]，状态语义见 [[ca_fee_order_status]]。

**边界（易混淆）**：企业维度以 [[ca_fee_company]] 的 `certification_no` 一行汇总，不能以订单行代替企业状态；统计「有多少企业已缴」应走企业主数据而非订单表。

## 需求背景

订单作为签署、支付、开票与台账编辑的操作载体，需要稳定业务编号；企业主数据则承担跨项目、跨角色的汇总职责，二者分层是收费模型的基础。

## 版本演进

- v0（本页）：建立术语桥与边界。