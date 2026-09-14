---
type: rule
title: 经办人DELETE仅冻结经办人角色
page_key: operator-delete-freeze-only
domain: 平台事件监听与同步
status: draft
aliases:
  - syncOperatorUser 删除规则
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustSyncEventProvider.java:syncOperatorUser
contract_version: "0.1"
belong: rules
---

删除规则：同一手机号既有经办人又有管理员时，DELETE 仅将经办人记录 `enable` 置 N 并冻结其 accountNormal 角色关联（`is_freeze='Y'`），不动管理员。

## 需求背景
手机号是联系人的自然标识，一人多角色常见。若删除经办人时连同管理员一并冻结，会误伤管理员权限；因此删除必须限定在经办人记录与其 accountNormal 关联上。涉及的过滤口径见 [[calibers/valid-contact-person]] 与 [[calibers/operator-role-rel-not-frozen]]。

## 版本演进
- v0 契约：规则取自 `CustSyncEventProvider.syncOperatorUser`；「accountNormal」角色关联的冻结范围未在语义分析中进一步展开。

```ground:rule
name: 经办人DELETE仅冻结经办人角色
content: "同一手机号既有经办人又有管理员时，DELETE 仅将经办人记录 enable 置N并冻结其 accountNormal 角色关联（is_freeze=Y），不动管理员"
impact: 避免误冻管理员权限
field_targets:
  - cust_person_info.enable
  - sys_cust_user_rel.is_freeze
evidence: "CustSyncEventProvider.java:syncOperatorUser"
related_pages:
  - tables/cust_person_info
  - tables/sys_cust_user_rel
  - calibers/operator-role-rel-not-frozen
```