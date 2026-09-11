---
type: entity
title: sso_system表
created: 2026-08-28
updated: 2026-08-28
tags: [sso, 数据库, 配置, 系统表]
related: [系统配置驱动, sso-code-provider, login-captcha-ck]
sources: ["需求文档/SSO验证码登录改造技术设计.docx"]
---
# sso_system表

`sso_system` 是SSO系统中的数据库表，用于存储各个业务系统（渠道）的配置信息。在验证码登录改造中，其 `captcha` 字段是实现 [[系统配置驱动]] 的关键。

## 关键字段

- **`captcha`**：整型字段，用于控制该系统渠道是否需要验证码。
  - `0`：表示可以不加验证码。
  - `1`：表示需要图片验证码或行为验证码。

## 在验证码流程中的应用

- **查询接口**：通过 `ssoSystemservice.getByChannel(sysChannel)` 方法根据系统渠道查询配置。
- **使用位置**：
  - 在 [[sso-code-provider]] 的 `validateCaptcha` 接口中，用于决定当验证码参数不完整时是否允许通过。
  - 在 [[login-captcha-ck]] 的 `checkCaptcha` 方法中，用于决定当未传入验证码参数时是否抛出异常。