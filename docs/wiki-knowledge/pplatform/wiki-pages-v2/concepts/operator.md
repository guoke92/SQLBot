---
type: concept
title: 运营人员
page_key: operator
domain: 企业变更与运营变更
status: draft
aliases: [运营人, operator, 归属运营]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_person_info
  - db:cust_oper_change_record
  - code:OperChangeRecordApplication.java
contract_version: "0.1"
maps_to: cust_person_info.operator_id
field_targets:
  - cust_person_info.operator_id
adjudication: boundary
also_confused_with:
  - cust_company_info.manager_id
belong: concepts
field_targets: [cust_person_info.operator_id]
---

「运营人员」指联系人维度上绑定的运营人，落 [[cust_person_info]].`operator_id` / `operator_realname`，其变更历史见 [[cust_oper_change_record]]。

边界：`cust_person_info.operator_id` / `operator_realname` 为联系人维度的运营人员；`cust_company_info.manager_id` 为企业维度业务经理，两者不同表不同粒度。

## 需求背景

服务归属既可按企业维度指定业务经理，也可按联系人维度指定运营人；变更、通知、权限判断取错粒度会直接影响服务对象。

## 版本演进

v0.1：首次建立术语桥。

相关页面：[[cust_person_info]]、[[cust_oper_change_record]]、[[oper_change_query]]、[[cust_company_info]]。