---
type: concept
title: 运营人员变更记录
page_key: oper-change-record
domain: 企业变更与运营变更
status: draft
aliases: [操作运营变更, cust_oper_change_record]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_oper_change_record
  - code_path:OperChangeRecordApplication.java:queryByPersonId
contract_version: "0.1"
maps_to: cust_oper_change_record
field_targets: [cust_oper_change_record]
adjudication: boundary
also_confused_with: [cust_change_record]
belong: concepts
---

「运营人员变更记录」指 [[tables.cust_oper_change_record]]，记录企业联系人（经办人）所绑定运营人员的前后变更流水，分类维度为 `change_type`（手动/批量/资产审核同步/企业变更回调），见 [[processes.oper-change-type]]。它与 [[tables.cust_change_record]] 容易混淆：后者是企业信息变更申请单及其审批状态，与运营人员归属无关；前者不承载审批，只承载归属变化轨迹。

## 需求背景

企业变更回调会间接触发运营人员调整，两条链路在时间上相邻、在企业维度上相关，因此需要明确区分「企业信息改了什么」与「运营人员换成了谁」，查询口径见 [[rules.oper-change-record-query]]。

## 版本演进

v0.1：首次登记，边界判定来自字段语义分析。