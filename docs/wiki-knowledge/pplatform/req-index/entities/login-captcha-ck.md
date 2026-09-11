---
type: entity
title: LoginCaptchaCk
created: 2026-08-28
updated: 2026-08-28
tags: [sso, 登录, 验证码, 检查器]
related: [sso-code-provider, sso-cache-util, 行为验证码校验, 验证码缓存机制, sso-result-code-enum]
sources: ["需求文档/SSO验证码登录改造技术设计.docx"]
---
# LoginCaptchaCk

`LoginCaptchaCk` 是登录流程中的验证码检查器，负责在用户调用 `doLogin` 接口时执行验证码校验逻辑。

## 核心方法

### `checkCaptcha`

```java
public void checkCaptcha(SsoSystemDO ssoSystemDO, LoginForm loginForm, HttpServletRequest request)
```

**功能**：根据系统配置和传入的验证码参数，执行校验逻辑。

**执行流程**：
1.  **判断验证码类型**：检查 `loginForm` 中是否包含图片验证码（`imgCode`）或行为验证码参数（`challenge`, `validate`, `seccode`）。
2.  **图片验证码校验**：如果包含图片验证码，则执行图片验证码校验逻辑。
3.  **行为验证码校验**：
    - 首先，尝试直接调用 [[极验验证码]] 服务进行校验。
    - 如果直接校验失败，则调用 [[sso-cache-util]] 的 `checkBehaviorCaptchaCache` 方法检查缓存（[[验证码缓存机制]]）。
    - 若缓存检查通过，则允许登录；否则抛出错误码为 `10929` 的异常（参见 [[sso-result-code-enum]]）。
4.  **配置兜底**：如果系统配置要求验证码（`captcha=1`）但未传入任何验证码参数，则抛出错误码为 `10930` 的异常。