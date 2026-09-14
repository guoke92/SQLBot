---
type: process
title: 经办人冻结状态机
page_key: operator_freeze_flow
domain: 平台内部服务对接
status: draft
aliases:
  - 经办人冻结流转
  - sys_cust_user_rel.is_freeze 状态机
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
belong: processes
---

经办人冻结状态机描述 [[sys_cust_user_rel]] 上 `is_freeze` 字段的两个取值与冻结/解冻两个操作的对应关系。该字段是 Y/N 形布尔约定在关系表上的实例（见 [[yn_flag_convention]]），冻结与解冻由同一个操作入口按目标状态切换。

在权限判定链路上，未冻结状态是有效关联的必要条件，查询口径见 [[not_frozen_user_rel]]；同一用户可能持有多条关联（不同客户、不同产品），冻结只作用于被操作的那条关系，产品维度的判定见 [[current_product_rel]]。

## 需求背景
运营侧需要在不删除关系数据的前提下停用某个经办人，因此用冻结标志代替物理删除；权限类服务在检索关系时必须显式带上未冻结条件，否则被冻结的经办人仍会通过校验。

## 版本演进
- v0.1（本页）：状态取值与流转来自代码语义分析，取值来源为常量而非枚举类。

```ground:process
name: 经办人冻结状态机
field: sys_cust_user_rel.is_freeze
states:
  - value: N
    label: 未冻结
    source: code_const
  - value: Y
    label: 已冻结
    source: code_const
transitions:
  - from: N
    event: 冻结经办人
    to: Y
    evidence: "code_path:PlatFormUserApplication.java:freezeOrThawOperatorUser"
  - from: Y
    event: 解冻经办人
    to: N
    evidence: "code_path:PlatFormUserApplication.java:freezeOrThawOperatorUser"
```