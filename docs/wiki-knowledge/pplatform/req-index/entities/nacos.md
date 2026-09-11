---
type: entity
title: Nacos
created: 2026-08-28
updated: 2026-08-28
tags: [基础设施, 配置中心, 服务发现]
related: [白名单机制]
sources: ["需求文档/SSO验证码登录改造技术设计.docx"]
---
# Nacos

Nacos是阿里巴巴开源的动态服务发现、配置管理和服务管理平台。在SSO验证码登录改造中，它被用作配置中心，用于管理验证码的 [[白名单机制]]。

## 在验证码改造中的应用

- **配置项**：`behaviorCaptchaWhitelistSysChannel`，存储允许绕过验证码校验的系统渠道正则表达式列表。
- **读取时机**：在 [[sso-code-provider]] 的 `validateCaptcha` 接口中，当行为验证码参数不完整时读取此配置。
- **管理方式**：运维人员可以通过Nacos控制台动态修改白名单规则，无需重启服务。