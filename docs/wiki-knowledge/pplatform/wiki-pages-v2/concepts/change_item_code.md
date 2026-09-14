---
type: concept
title: 变更项编码
page_key: change_item_code
domain: 企业变更与运营变更
status: draft
aliases: [itemCode, UN编码, 变更项 code]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_change_cfg
  - db:cust_change_record
  - code:CustChangeApplication.java
contract_version: "0.1"
maps_to: cust_change_cfg.item_code
field_targets:
  - cust_change_cfg.item_code
adjudication: boundary
also_confused_with:
  - cust_change_record.alter_type_id
  - cust_change_record.alter_data
belong: concepts
field_targets: [cust_change_cfg.item_code]
---

「变更项编码」在口语中常被简称为「变更项」，但它特指配置字典编码：`cust_change_cfg.item_code`，取值 UN0001~UN0016（[[cust_change_cfg]]）。判定某个变更是否包含某项能力时，正确链路是 `alter_type_id` → `cust_change_cfg.id` → `item_code`（[[change_item_contains]]），而不是直接比较记录上的字段。

边界：`item_code` 是配置字典编码（UN0001~UN0016）；[[cust_change_record]].`alter_type_id` 是 `cust_change_cfg.id` 的逗号分隔列表；`alter_data` 是编码的 JSON 数组快照。三者不可互换。

## 需求背景

变更项需要在端、认证方式、客户类型、总公司维度上分别配置，同时又要跨端对齐名称不一致的项（`plat_item` vs `oper_item`），因此引入稳定编码作为唯一语义键。

## 版本演进

v0.1：首次建立术语桥；本页暂无历史版本差异记录。

相关页面：[[cust_change_cfg]]、[[change_item_contains]]、[[admin_mobile_change_items]]、[[cust_change_record]]。