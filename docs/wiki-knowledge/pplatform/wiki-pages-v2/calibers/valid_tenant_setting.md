---
type: caliber
title: 有效租户配置
page_key: valid_tenant_setting
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 启用态租户配置
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:getTenantSetting
  - code:SaaSAuthController.java:logout
contract_version: "0.1"
belong: calibers
---

口径“有效租户配置”用于登录/登出取租户配置：只有 enable='Y' 的 [[tenant_setting_config]] 记录可用。

## 需求背景

租户配置存在历史数据与停用记录，登录/登出、菜单、验证码策略都必须只认启用态，
否则会取到过期的 SSO 渠道或统码。

## 版本演进

- v0（草稿）：口径来自代码查询条件。

```ground:caliber
name: 有效租户配置
predicate: "tenant_setting_config.enable = 'Y'"
scope: getTenantSetting / logout 查询租户配置
evidence: "code_path:SaaSAuthController.java:getTenantSetting + SaaSAuthController.java:logout"
```

相关：[[tenant_setting_config]]、[[tenant_setting_by_db_tenant_code]]、[[login_captcha_policy]]。