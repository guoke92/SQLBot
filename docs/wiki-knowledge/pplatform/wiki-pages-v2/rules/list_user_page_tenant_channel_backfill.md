---
type: rule
title: 租户 SSO 渠道回填用户查询
page_key: list_user_page_tenant_channel_backfill
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 用户列表回填统码
oid: 1
scope:
  databases: [unknown]
sources:
  - code:LocalTypeUserController.java:listUserPage
  - code:LocalTypeUserController.java:getDbTenantCodeById
contract_version: "0.1"
belong: rules
---

用户列表查询需由 custId 反查租户编码，再取租户统码回填 DTO，供下游跨系统查询用户。

## 需求背景

用户列表跨租户/跨 SSO 系统查询依赖该回填：企业 → [[cust_company_info.db_tenant_code]] →
租户统码 [[tenant_setting_config.sso_tenant_chanel]] → userDTO.ssoSysChannel
（术语边界见 [[tenant_sso_chanel]]、[[sys_channel]]）。

## 版本演进

- v0（草稿）：规则来自代码回填链路。

```ground:rule
name: 租户 SSO 渠道回填用户查询
content: "listUserPage 由 custId 反查 cust_company_info.db_tenant_code，再取租户 ssoTenantChanel 写入 userDTO.ssoSysChannel，供下游按租户统码跨系统查询用户。"
impact: "用户列表跨租户/跨 SSO 系统查询依赖该回填。"
field_targets:
  - cust_company_info.db_tenant_code
  - tenant_setting_config.sso_tenant_chanel
evidence: "code_path:LocalTypeUserController.java:listUserPage + getDbTenantCodeById"
```

相关：[[cust_company_info]]、[[tenant_setting_config]]、[[tenant_sso_chanel]]、[[sys_channel]]。