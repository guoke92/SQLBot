---
type: rule
title: 经办人信息以 sys_user + sso_user 为准
page_key: person_info_source_of_truth
domain: 平台内部服务对接
status: draft
aliases:
  - 经办人信息基准
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_person_info.name / user_name / email]
  - semantic:field_semantics[sys_user / sso_user]
contract_version: "0.1"
belong: rules
---

联系人姓名、登录名、业务邮箱的权威来源是 sys_user + sso_user；仅当联系人侧自身为空时才由经办人新增流程补全，业务邮箱变更时按条件回写登录邮箱。

## 需求背景

这条规则决定了 [[tables/cust_person_info]] 与 [[tables/sys_user_sso_user]] 的主从关系，避免两边都有值时互相覆盖。

## 版本演进

v0：首次成页。

```ground:rule
name: 经办人信息以 sys_user + sso_user 为准
field: cust_person_info.name / user_name / email
condition: "a) 仅本身为空时 b) 业务邮箱变更时"
effect: "由经办人新增流程补全 / 按条件回写登录邮箱，基准为用户中心与 SSO"
evidence: code
```