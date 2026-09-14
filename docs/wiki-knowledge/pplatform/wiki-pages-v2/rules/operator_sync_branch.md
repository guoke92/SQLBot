---
type: rule
title: 经办人同步操作分支规则
page_key: operator_sync_branch
domain: 平台事件监听与同步
status: draft
aliases:
  - syncOperatorUser 分支
  - 经办人增删改冻
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:CustSyncEventProvider.java:syncOperatorUser
contract_version: "0.1"
belong: rules
---

经办人事件按操作类型分流：INSERT/UPDATE 走新增与编辑，FREEZE/THAW/DELETE 走冻结、解冻与删除。

## 需求背景

需求文档主张「用户邀请→激活→同步用户到 SSO、同步用户到 AMS 运营中台」，代码侧由 `CustSyncEventProvider.syncOperatorUser` 承接并经 `CustSyncService` 广播。DELETE 分支的特别之处在于：同手机号既为经办人又为管理员时，仅将经办人记录 `enable=N` 并冻结其对 `accountNormal` 角色的关联（[[operator_freeze_scope]]、[[sys_cust_user_rel]]），人员侧写法见 [[cust_person_info]]。落库的人员类型使用 `UserTypeEnum.getDictKey()`。

## 版本演进

- 冻结值改用 `UserFreezeEnum.FREEZE.getDictKey()`，与人员表 `EnableEnum.N.name()` 风格不同。
- 同步范围由 `syncByRoleOn` 控制，见 [[cust_sync_by_role]]。

```ground:rule
name: 经办人同步操作分支
content: INSERT/UPDATE→addOperator/editOperator；FREEZE/THAW/DELETE→走冻结/解冻；DELETE 且同手机号既为经办人又为管理员时，仅将经办人记录 enable=N 并冻结其对 accountNormal 角色的 SysCustUserRel
impact: 避免误冻管理员权限
field_targets:
  - cust_person_info.enable
  - sys_cust_user_rel.is_freeze
evidence: "code_path:CustSyncEventProvider.java:syncOperatorUser + reqdoc:用户邀请→激活→同步用户到 SSO、同步用户到 AMS 运营中台"
```