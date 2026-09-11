---
type: rule
title: 运营中台鉴权签名 md5(secret + sysChannel + loginName)
page_key: rule.token_sign_md5
domain: 平台内部服务对接
status: draft
aliases:
  - 鉴权签名规则
  - token 签名
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[tenant_setting_config.platform_secret_key]
  - semantic:field_semantics[tenant_setting_config.sso_tenant_chanel]
contract_version: "0.1"
---

请求运营中台 token 时，签名由 platform_secret_key、sysChannel、loginName 三者拼接后做 md5 得到。

## 需求背景

三个入参分属不同来源：secret 与 sysChannel 来自租户配置（[[tables/tenant_setting_config]]，见 [[concepts/db_tenant_code_bridge]]），loginName 来自用户身份（[[tables/sys_user_sso_user]]）。任一取值不正确都会导致鉴权失败。

## 版本演进

v0：首次成页。

```ground:rule
name: 运营中台鉴权签名 md5(secret + sysChannel + loginName)
field: tenant_setting_config.platform_secret_key
condition: "请求运营中台 token"
effect: "md5(secret+sysChannel+loginName)"
evidence: code
```