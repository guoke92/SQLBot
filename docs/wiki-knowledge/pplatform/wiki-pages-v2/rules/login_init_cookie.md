---
type: rule
title: 登录初始化写入企业上下文 Cookie
page_key: login_init_cookie
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - init 写 Cookie
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:init
contract_version: "0.1"
belong: rules
---

SSO 登录初始化成功后，必须把当前企业上下文写入 Cookie 与缓存。

## 需求背景

前端与网关后续请求依赖这些 Cookie/缓存识别当前企业与租户；企业上下文来自
[[cust_company_info.db_tenant_code]]，并与 [[login_user_status_state]] 的 NORMAL 态同步产生。

## 版本演进

- v0（草稿）：规则来自 init 代码证据。

```ground:rule
name: 登录初始化写入企业上下文 Cookie
content: "init 成功后写 fbpccid/fbpcctype/fbpccname(URL编码)/dbtenantCode/fbpcccode 五个 Cookie，并把 companyId/companyType/companyName/companyCode 回填 LoginUser 并写入 Redis。"
impact: "前端与网关后续请求依赖这些 Cookie/缓存识别当前企业与租户。"
field_targets:
  - cust_company_info.db_tenant_code
  - sys_cust_user_rel.is_freeze
evidence: "code_path:SaaSAuthController.java:init"
```

相关：[[login_user_status_state]]、[[cust_company_info]]、[[db_tenant_code]]。