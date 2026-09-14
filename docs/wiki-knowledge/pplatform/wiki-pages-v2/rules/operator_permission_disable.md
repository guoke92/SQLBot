---
type: rule
title: 经办人无产品权限时 enable 置 'N'，解冻恢复 'Y'
page_key: operator_permission_disable
domain: 平台内部服务对接
status: draft
aliases:
  - 经办人权限置无效
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_person_info.enable]
  - semantic:state_machines[经办人产品关联冻结状态]
contract_version: "0.1"
belong: rules
---

当经办人失去产品权限时，联系人记录的 enable 被置为 'N'；解冻后恢复为 'Y'。

## 需求背景

这是联系人侧 enable 与产品授权冻结状态（[[processes/operator_freeze_machine]]、[[tables/sys_cust_user_rel]]）的联动点。因此在联系人有效性判定中，enable 与 status 需一并考虑（[[calibers/person_effective_status]]）。

## 版本演进

v0：首次成页。

```ground:rule
name: 经办人无产品权限时 enable 置 'N'，解冻恢复 'Y'
field: cust_person_info.enable
condition: "经办人无产品权限"
effect: "置 'N'；解冻时恢复 'Y'"
evidence: code
```