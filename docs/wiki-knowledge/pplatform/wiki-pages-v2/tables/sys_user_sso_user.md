---
type: table
title: sys_user / sso_user（用户中心与 SSO 用户表）
page_key: sys_user_sso_user
domain: 平台内部服务对接
status: draft
aliases:
  - sys_user
  - sso_user
  - 用户中心表
oid: 1
scope:
  databases: [lowcode_pplatform]
sources:
  - semantic:field_semantics[sys_user / sso_user]
contract_version: "0.1"
belong: tables
---

用户中心（sys_user）与 SSO（sso_user）两张表在语义分析中作为同一组用户身份字段来源给出，是经办人信息的事实基准。

## 需求背景

[[tables/cust_person_info]] 的姓名/登录名/业务邮箱仅在自身为空时才由经办人新增流程补全，其权威来源是本组表（见 [[rules/person_info_source_of_truth]]）。user_id 与 [[tables/cust_person_info]] 的 user_id 指向 sys_user 主键。

## 版本演进

v0：首次成页；按语义分析给出的合并条目收录字段，未拆分为两页。

