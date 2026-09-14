---
type: rule
title: 登录用户信息同步 SSO 邮箱
page_key: update_cust_person_sso_email
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 邮箱同步 SSO
oid: 1
scope:
  databases: [unknown]
sources:
  - code:UserInfoFacade.java:updateCustPerson
contract_version: "0.1"
belong: rules
---

更新用户邮箱后，需在满足条件时把邮箱回写 SSO 侧。

## 需求背景

保证 SSO 侧邮箱与 [[sys_user.email]] 一致：仅当 [[sys_user.sso_user_id]] 非空且 sso_user.email
为空时回写，并带 orgCode RpcContext 透传（[[org_code]]）。

## 版本演进

- v0（草稿）：规则来自代码回写条件。

```ground:rule
name: 登录用户信息同步 SSO 邮箱
content: "updateCustPerson 更新 sys_user 邮箱后，若 sys_user.sso_user_id 非空且 sso_user.email 为空，则回写 sso_user.email（带 orgCode RpcContext 透传）。"
impact: "保证 SSO 侧邮箱与 sys_user 一致。"
field_targets:
  - sys_user.email
  - sys_user.sso_user_id
evidence: "code_path:UserInfoFacade.java:updateCustPerson"
```

相关：[[sys_user]]、[[org_code]]、[[update_agw_login_email]]。