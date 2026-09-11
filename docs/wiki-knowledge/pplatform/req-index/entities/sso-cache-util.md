---
type: entity
title: SsoCacheUtil
created: 2026-08-28
updated: 2026-08-28
tags: [sso, 工具类, 缓存, redis]
related: [sso-code-provider, login-captcha-ck, 验证码缓存机制, 参数一致性校验, 一次性使用]
sources: ["需求文档/SSO验证码登录改造技术设计.docx"]
---
# SsoCacheUtil

`SsoCacheUtil` 是一个工具类，专门封装了与行为验证码缓存相关的操作逻辑，是 [[验证码缓存机制]] 的具体实现者。

## 核心方法

### `checkBehaviorCaptchaCache`

```java
public boolean checkBehaviorCaptchaCache(String loginName, String sysChannel,
                                         String challenge, String validate, String seccode)
```

**功能**：检查缓存中是否存在有效的、参数一致的验证码校验结果。

**逻辑**：
1.  根据 `loginName` 和 `sysChannel` 生成缓存键（`sso:behavior_captcha:{loginName}#{sysChannel}`），从 [[redis]] 获取缓存值。
2.  若缓存不存在，返回 `false`。
3.  若传入了完整的验证码参数，则将其拼接（`challenge|validate|seccode`），与缓存值进行字符串比较（[[参数一致性校验]]）。
4.  若比较一致，则删除缓存（[[一次性使用]]）并返回 `true`；否则返回 `false`。

## 缓存键格式

- **前缀**：`sso:behavior_captcha:` (定义于 `SSOConstants.BEHAVIOR_CAPTCHA_CACHE_KEY_PREFIX`)
- **完整键**：`sso:behavior_captcha:{loginName}#{sysChannel}`