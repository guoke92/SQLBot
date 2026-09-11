---
type: process
title: 运营人员变更类型（cust_oper_change_record.change_type）
page_key: process.oper-change-type
domain: 企业变更与运营变更
status: draft
aliases: [change_type, 运营变更类型枚举, CHANGE_TYPE_DESC]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_oper_change_record
  - code_path:OperChangeRecordApplication.java:CHANGE_TYPE_DESC
contract_version: "0.1"
---

`change_type` 是 [[tables.cust_oper_change_record]] 上的分类字段，取值集合由代码字典 `CHANGE_TYPE_DESC` 给出：`MANUAL`=手动变更、`BATCH`=批量变更、`AUTO_ASSIGN`=自动分配、`AUTO_UPDATE`=自动更新、`ASSET_AUDIT_SYNC`=资产审核同步、`CUST_CHANGE_CALLBACK`=企业变更回调。字典映射与未命中回显规则见 [[rules.oper-change-type-dict]]。

## 需求背景

运营人员变更来源分散在人工操作、批量任务、资产审核同步与企业变更回调等多条链路，本字段是这些链路在流水上的统一归类维度，前端展示名由字典映射；映射未命中时直接回显原值，保证新增来源不丢数据。

## 版本演进

v0.1：首次登记。该状态机当前无状态迁移语义，仅登记取值集合（transitions 为空）。

```ground:process
name: 运营人员变更类型
field: cust_oper_change_record.change_type
states:
  - value: MANUAL
    label: 手动变更
    source: code_enum
  - value: BATCH
    label: 批量变更
    source: code_enum
  - value: AUTO_ASSIGN
    label: 自动分配
    source: code_enum
  - value: AUTO_UPDATE
    label: 自动更新
    source: code_enum
  - value: ASSET_AUDIT_SYNC
    label: 资产审核同步
    source: code_enum
  - value: CUST_CHANGE_CALLBACK
    label: 企业变更回调
    source: code_enum
transitions: []
```