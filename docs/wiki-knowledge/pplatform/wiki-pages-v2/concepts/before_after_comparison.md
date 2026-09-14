---
type: concept
title: 变更前后信息对比
page_key: before_after_comparison
domain: 企业变更与运营变更
status: draft
aliases: [oldPersonId/personId, 变更前后对比, oper_cust_info 对比]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_change_record
  - db:cust_oper_change_record
  - code:CustChangeApplication.java
contract_version: "0.1"
maps_to: cust_change_record.oper_cust_info
field_targets:
  - cust_change_record.oper_cust_info
adjudication: boundary
also_confused_with:
  - cust_oper_change_record.before_operator_id
belong: concepts
field_targets: [cust_change_record.oper_cust_info]
---

「变更前后信息对比」默认指 [[cust_change_record]].`oper_cust_info`——运营中台返回的客户信息 JSON，其中 `personId` 为变更后管理员、`oldPersonId` 为变更前管理员，用于管理员手机号变更的判定与跳转（[[admin_mobile_redirect]]）。

边界：`oper_cust_info` 是运营中台返回的 JSON（含 `personId` / `oldPersonId`）；[[cust_oper_change_record]].`before_operator_id`/`after_operator_id` 是运营人员变更的独立结构化字段。一侧需解析 JSON，一侧可直接比较，不可互换。

## 需求背景

管理员变更发生在运营中台侧，平台需要拿到变更前后的管理员身份才能判断登录人手机号是否失效，因此以 JSON 快照形式留存并本地解析。

## 版本演进

v0.1：首次建立术语桥。

相关页面：[[cust_change_record]]、[[admin_mobile_redirect]]、[[cust_oper_change_record]]、[[operator]]、[[cust_person_info]]。