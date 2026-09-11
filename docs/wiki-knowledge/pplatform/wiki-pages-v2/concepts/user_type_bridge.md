---
type: concept
title: 联系人用户类型术语桥（admin / operator / guest）
page_key: concept.user_type_bridge
domain: 平台内部服务对接
status: draft
aliases:
  - user_type
  - admin
  - operator
  - guest
  - 客户管理员
  - 经办人
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_person_info.user_type]
  - semantic:field_semantics[cust_person_info.operator_id / operator_realname / operator]
contract_version: "0.1"
maps_to:
  - term: admin
    target: cust_person_info.user_type
    evidence: code
  - term: operator
    target: cust_person_info.user_type
    evidence: code
  - term: guest
    target: cust_person_info.user_type
    evidence: code
field_targets:
  - cust_person_info.user_type
  - cust_person_info.operator_id
  - cust_person_info.operator_realname
  - cust_person_info.operator
also_confused_with:
  - cust_person_info.operator
---

联系人 user_type 三值：admin（客户管理员）、operator（经办人）、guest（游客）。注意它与运营人员字段 operator（运营登录名）同名不同义。

## 需求背景

「经办人」既可作为 user_type 的取值，也可指联系人在产品权限语境下的角色，其可用性由 enable 与冻结状态共同决定（[[processes/operator_freeze_machine]]）。运营人员信息（operator_id / operator_realname / operator）来自资产审核侧同步，不参与用户身份判定。

## 版本演进

v0：首次成页。