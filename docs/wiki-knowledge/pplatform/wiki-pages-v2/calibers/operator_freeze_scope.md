---
type: caliber
title: 经办人角色冻结口径
page_key: operator_freeze_scope
domain: 平台事件监听与同步
status: draft
aliases:
  - 经办人冻结范围
  - is_freeze=Y 口径
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:CustSyncEventProvider.java:syncOperatorUser
contract_version: "0.1"
belong: calibers
---

删除经办人时的冻结范围口径：只冻结经办人记录对应的 `accountNormal` 角色关联，即 [[sys_cust_user_rel]].`is_freeze='Y'`，不动管理员。

## 需求背景

同手机号既为经办人又为管理员时，若按用户维度整体冻结会误伤管理员权限；因此改为按记录维度：经办人记录 `enable=N`（见 [[cust_person_info]]），并仅冻结其对 `accountNormal` 的关联。分支细节见 [[operator_sync_branch]]。

## 版本演进

- 冻结值使用 `UserFreezeEnum.FREEZE.getDictKey()`，与人员表 `EnableEnum.N.name()` 的落库风格不同，跨表核对时需按各自风格取值。
- 该口径只覆盖 DELETE 事件；FREEZE/THAW 走独立的冻结/解冻分支。

```ground:caliber
name: 经办人角色冻结口径
predicate: "sys_cust_user_rel.is_freeze = 'Y'"
scope: DELETE 且同手机号既为经办人又为管理员时，仅冻结经办人记录对应 accountNormal 角色关联
evidence: "code:CustSyncEventProvider.java:syncOperatorUser"
```