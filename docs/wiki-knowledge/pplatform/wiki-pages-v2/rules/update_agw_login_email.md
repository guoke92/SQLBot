---
type: rule
title: AGW 网关更新邮箱免登录态
page_key: update_agw_login_email
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 网关代更新邮箱
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:updateAgwLoginEmail
contract_version: "0.1"
belong: rules
---

AGW 网关侧更新邮箱接口直接用入参 userId 更新，不校验登录态；普通接口取当前登录用户。

## 需求背景

网关侧可代更新邮箱（[[sys_user.email]]），需注意越权风险；与自助更新
（updateLoginEmail 取当前登录用户）行为不同，两者不可混用。

## 版本演进

- v0（草稿）：规则来自代码实现差异。

```ground:rule
name: AGW 网关更新邮箱免登录态
content: "updateLoginEmail 取当前登录用户；updateAgwLoginEmail 直接以入参 userId 更新邮箱，不校验登录态。"
impact: "网关侧可代更新邮箱，需注意越权风险。"
field_targets:
  - sys_user.email
evidence: "code_path:SaaSAuthController.java:updateAgwLoginEmail"
```

相关：[[sys_user]]、[[update_cust_person_sso_email]]。