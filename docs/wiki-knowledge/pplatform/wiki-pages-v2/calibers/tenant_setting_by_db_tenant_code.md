---
type: caliber
title: 按数据租户查询租户配置
page_key: tenant_setting_by_db_tenant_code
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 租户配置查库键
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:getTenantSetting
contract_version: "0.1"
belong: calibers
---

口径“按数据租户查询租户配置”：以当前线程租户编码
（`MetaDataThreadLocalConfig.getDbTenantCode()`）匹配 [[tenant_setting_config.db_tenant_code]]，
再叠加启用态（[[valid_tenant_setting]]）。

## 需求背景

登录/登出、菜单与验证码策略需要在多租户下正确取到本租户配置，租户键必须来自线程上下文而非入参，
避免跨租户取值。

## 版本演进

- v0（草稿）：口径来自代码查询条件。

```ground:caliber
name: 按数据租户查询租户配置
predicate: "tenant_setting_config.db_tenant_code = MetaDataThreadLocalConfig.getDbTenantCode()"
scope: 登录/登出、菜单、验证码策略
evidence: "code_path:SaaSAuthController.java:getTenantSetting"
```

相关：[[tenant_setting_config]]、[[db_tenant_code]]、[[valid_tenant_setting]]。