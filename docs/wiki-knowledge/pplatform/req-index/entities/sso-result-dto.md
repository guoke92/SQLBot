---
type: entity
title: SSOResultDTO
created: 2026-08-28
updated: 2026-08-28
tags: [SSO, DTO, 数据传输对象, Java]
related: [sso-result-code-enum, passwordutils]
sources: ["需求文档/SSO单点登录系统安全设计文档.docx"]
---

# SSOResultDTO

## 概述

SSOResultDTO 是SSO单点登录系统的统一返回数据结构（Data Transfer Object），用于包装所有系统操作的结果信息。

## 结构说明

SSOResultDTO 为泛型类 `SSOResultDTO<T>`，主要包含：

- **错误码**：引用 [[sso-result-code-enum]] 中定义的错误码
- **消息信息**：可动态设置的描述信息，支持通过 `setMessage()` 方法自定义

## 使用示例

```java
// 返回错误
return new SSOResultDTO<>(SSOResultCodeEnum.ERROR_CODE_10918);

// 返回带自定义消息的结果
SSOResultDTO<String> result = new SSOResultDTO<>(SSOResultCodeEnum.CORRECT_CODE_20904);
result.setMessage(String.format(result.getMessage(), plusDays));
return result;
```

## 应用场景

- 密码强度验证结果返回
- 登录操作结果返回
- 会话状态检查结果返回
- 密码过期检查结果返回
- 账户锁定状态返回

## 相关实体

- [[sso-result-code-enum]]：错误码枚举定义
- [[passwordutils]]：密码验证工具类