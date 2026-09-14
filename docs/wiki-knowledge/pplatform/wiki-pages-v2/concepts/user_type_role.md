---
type: concept
title: 用户类型 user_type
page_key: user_type_role
domain: 经办人/联系人/管理员管理
status: draft
aliases:
  - 用户类型术语桥
  - accountAdmin/accountNormal/accountGuest
oid: 1
scope:
  databases:
    - lowcode_pplatform
sources:
  - code
contract_version: "0.1"
maps_to:
  - cust_person_info.user_type
field_targets:
  - cust_person_info.user_id
adjudication: >
  联系人记录通过 cust_person_info.user_type 区分 accountAdmin / accountNormal / accountGuest
  三类用户（Java 名是 admin / operator / guest，落库是 UserTypeEnum.getDictKey()）；
  识别管理员与经办人分别使用 cust_person_info.user_type = 'accountAdmin' 与
  cust_person_info.user_type = 'accountNormal'。
also_confused_with:
  - cust_person_info.company_type
  - sys_cust_user_rel.cust_type
  - cust_user_rel.user_type
belong: concepts
---

「用户类型」把企业下的人员区分为管理员、经办人、游客三类，落在 [[cust_person_info]] 的 `user_type` 上。Java 常量名是 `admin` / `operator` / `guest`，**落库键是 dictKey**：`accountAdmin` / `accountNormal` / `accountGuest`。问数过滤必须用后者。旧表 [[cust_user_rel]] 抽样仍可见 `user_type='accountAdmin'`，不要和人员主表混用。它是 [[admin_user]] 与 [[operator_user]] 两个口径的共同取值域。

## 需求背景
平台侧需要按用户类型裁剪可见功能与可执行动作：管理员承担企业确认等管理动作，经办人被纳入关系冻结管理。因此类型字段必须在建档时确定，并在人员列表查询中与有效性口径 [[valid_person]] 一起使用。

## 版本演进
- v0.2：纠正 Java 名与 dictKey 混用；人员主表以 DB 实测 `accountAdmin` 为准。
