---
type: concept
title: 变更方式
page_key: alter_mode
domain: 企业变更与运营变更
status: draft
aliases: [alterMode, 平台变更, 企业自行变更]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_change_record
  - code:CustChangeApplication.java
contract_version: "0.1"
maps_to: cust_change_record.alter_mode
field_targets:
  - cust_change_record.alter_mode
adjudication: synonym
also_confused_with: []
belong: concepts
field_targets: [cust_change_record.alter_mode]
---

「变更方式」即 [[cust_change_record]].`alter_mode`，标识这次变更是谁发起的：1=平台变更（PLAT_ALTER），2=企业自行变更（SELF_ALTER），由 `AlterModeEnum.getDictKey` 落库。

## 需求背景

同一次变更在平台代客操作与企业自助操作下的材料要求、通知对象不同，需要独立字段留存发起方式，且必须落字典键值而非枚举名。

## 版本演进

v0.1：首次建立术语桥。

相关页面：[[cust_change_record]]、[[customer_change]]、[[change_status]]。