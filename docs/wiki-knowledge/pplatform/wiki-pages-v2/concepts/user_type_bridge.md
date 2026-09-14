---
type: concept
title: 联系人用户类型术语桥（accountAdmin / accountNormal / accountGuest）
page_key: user_type_bridge
domain: 经办人/联系人/管理员管理
status: draft
aliases:
  - user_type
  - accountAdmin
  - accountNormal
  - accountGuest
  - 客户管理员
  - 经办人
oid: 1
scope:
  databases: [lowcode_pplatform]
sources:
  - semantic:field_semantics[cust_person_info.user_type]
  - code:UserTypeEnum
contract_version: "0.1"
maps_to:
  - term: admin
    target: cust_person_info.user_type
    evidence: code
    stored_as: accountAdmin
  - term: operator
    target: cust_person_info.user_type
    evidence: code
    stored_as: accountNormal
  - term: guest
    target: cust_person_info.user_type
    evidence: code
    stored_as: accountGuest
field_targets:
  - cust_person_info.user_type
  - cust_person_info.operator_id
  - cust_person_info.operator_realname
  - cust_person_info.operator
also_confused_with:
  - cust_person_info.operator
belong: concepts
---

联系人 `user_type` 三值（`UserTypeEnum.getDictKey()`）：`accountAdmin`（客户管理员）、`accountNormal`（经办人）、`accountGuest`（游客）。Java 名 `admin` / `operator` / `guest` 不是人员主表的落库键。注意它与运营人员字段 `operator`（运营登录名）同名不同义。

## 需求背景

「经办人」既可作为 user_type 的取值（`accountNormal`），也可指联系人在产品权限语境下的角色，其可用性由 enable 与冻结状态共同决定（[[processes/operator_freeze_machine]]）。运营人员信息（operator_id / operator_realname / operator）来自资产审核侧同步，不参与用户身份判定。

## 版本演进

v0.2：按 dictKey 重写术语桥，避免按 Java 名过滤得到空集。
