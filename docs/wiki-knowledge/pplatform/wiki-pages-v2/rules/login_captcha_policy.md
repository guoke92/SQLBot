---
type: rule
title: 登录图形验证码策略
page_key: login_captcha_policy
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 图形验证码策略
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:resolveNeedLoginCaptcha
  - reqdoc:login-captcha-scene
contract_version: "0.1"
belong: rules
---

登录是否需要图形验证码由环境与 SSO 系统渠道配置共同决定。

## 需求背景

文档主张“登录验证码场景：测试环境可配置 SSO 系统 captcha 决定是否需要图形验证码”，
代码已确认：非 qa/qa2 一律需要验证码；qa/qa2 查 [[sys_channel]] 对应 SsoSystemDO.captcha，
captcha==0 可免验证码。生产始终开启，测试环境按渠道配置放开。

## 版本演进

- v0（草稿）：规则同时有代码与需求文档来源（双源）。

```ground:rule
name: 登录图形验证码策略
content: "非 qa/qa2 环境一律需要验证码；qa/qa2 下查 SsoSystemDO.captcha，captcha==0 表示可不加验证码（返回 false），其余（含查询异常）返回 true。"
impact: "仅测试环境允许免图形验证码，生产始终开启。"
field_targets:
  - open_sso_channel.sys_channel
evidence: "code_path:SaaSAuthController.java:resolveNeedLoginCaptcha + reqdoc:login-captcha-scene"
```

相关：[[open_sso_channel]]、[[sys_channel]]、[[tenant_setting_config]]。