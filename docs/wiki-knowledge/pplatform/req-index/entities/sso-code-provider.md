---
type: entity
title: SsoCodeProvider
created: 2026-08-28
updated: 2026-08-28
tags: [sso, 接口, 验证码, 核心组件]
related: [sso-cache-util, login-captcha-ck, 行为验证码校验, 系统配置驱动, 白名单机制]
sources: ["需求文档/SSO验证码登录改造技术设计.docx"]
---
# SsoCodeProvider

`SsoCodeProvider` 是SSO验证码登录改造中的核心接口，定义了行为验证码校验的契约。其主要实现类为 `SsoCodeProviderImpl`。

## 核心方法

### `validateCaptcha`

```java
boolean validateCaptcha(String loginName, int second, String sysChannel,
                        String challenge, String validate, String seccode,
                        boolean loginCaptcha, String imageSerialNo, String imgCode);
```

**功能**：校验行为验证码，并根据参数决定是否缓存结果。

**参数说明**：
- `loginName`：登录名，必填。
- `second`：缓存有效期（秒），必填。
- `sysChannel`：系统渠道，必填。
- `challenge`, `validate`, `seccode`：行为验证码参数，当需要行为验证码时必填。
- `imageSerialNo`, `imgCode`：图片验证码参数。
- `loginCaptcha`：是否缓存验证结果。`true` 表示缓存，`false` 表示不缓存。

**返回值**：`true` 表示校验成功，`false` 表示校验失败。

## 实现逻辑 (`SsoCodeProviderImpl`)

1.  **参数校验**：检查 `loginName` 和 `sysChannel` 是否为空。
2.  **配置与白名单检查**：若行为验证码参数不完整，先检查 [[白名单机制]]，再查询 [[sso_system表]] 的 `captcha` 配置（[[系统配置驱动]]）。
3.  **调用校验服务**：组装请求，调用 [[极验验证码]] 服务（`ssoLoginProvider.secondValidate`）进行校验。
4.  **缓存结果**：校验成功且 `loginCaptcha=true` 时，调用 [[sso-cache-util]] 将参数缓存至 [[redis]]。