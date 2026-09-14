---
type: process
title: 经办人冻结状态（SysCustUserRel）
page_key: operator_freeze_state
domain: 微信生态/小程序/扫脸
status: draft
aliases: [经办人冻结, is_freeze 状态]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:PlatFormUserApplication.java
  - code:CustSyncEventProvider.java
contract_version: "0.1"
belong: processes
---

# 经办人冻结状态（SysCustUserRel）

描述经办人账号在 sys_cust_user_rel.is_freeze 上的冻结 / 解冻流转。该状态参与 [[valid_contact]] 的过滤（`is_freeze='N'`），并影响扫脸主体有效性视图。

## 需求背景

运营中台同步删除经办人时，若同手机号兼管理员，只冻结经办人角色，避免误伤管理员账号。

## 版本演进

v0.1 记录 N/Y 两态与三条迁移路径。

```ground:process
state_machine: 经办人冻结状态（SysCustUserRel）
field: sys_cust_user_rel.is_freeze
states:
  - value: N
    label: 解冻/正常
    source: code_enum
  - value: Y
    label: 已冻结
    source: code_enum
transitions:
  - from: N
    event: freezeOrThawOperatorUser operationType=FREEZE
    to: Y
    evidence: code_path:PlatFormUserApplication.java#freezeOrThawOperatorUser
  - from: Y
    event: freezeOrThawOperatorUser operationType=THAW
    to: N
    evidence: code_path:PlatFormUserApplication.java#freezeOrThawOperatorUser
  - from: N
    event: 运营中台 syncOperatorUser OperatorType=DELETE（同手机号兼管理员时只冻经办人角色）
    to: Y
    evidence: code_path:CustSyncEventProvider.java#syncOperatorUser
```

相关：[[cust_person_info]]、[[valid_contact]]、[[face_intent_subject]]。