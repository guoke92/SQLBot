---
type: entity
title: PasswordUtils
created: 2026-08-28
updated: 2026-08-28
tags: [SSO, 密码验证, 工具类, Java]
related: [密码强度验证, sso-result-code-enum, sso-result-dto]
sources: ["需求文档/SSO单点登录系统安全设计文档.docx"]
---

# PasswordUtils

## 概述

PasswordUtils 是SSO单点登录系统中的核心密码强度验证工具类，负责在用户注册、密码修改等关键操作时强制执行密码复杂性验证。

## 核心功能

### 密码强度验证入口

通过 `matchesPassword(Integer pwdStrong, String password)` 方法进行密码强度验证，根据系统配置的密码强度等级（pwdStrong字段）调用对应的验证方法。

### 验证方法

| 方法 | 强度等级 | 要求 |
|------|---------|------|
| `matchesFor2(password)` | 等级2 | 8-15位，包含大写字母、小写字母、数字 |
| `matchesFor3(password)` | 等级3 | 8-15位，包含大写字母、小写字母、数字、特殊字符 |
| `matchesFor4(password)` | 等级4 | 8-32位，包含大写字母、小写字母、数字、特殊字符 |

### 返回值

- 验证通过：返回 `null`
- 验证失败：返回包含对应错误码的 [[sso-result-dto]] 对象（10918/10919/10927）

## 验证场景

- **用户注册**：新用户注册时强制验证密码强度
- **密码修改**：用户修改密码时强制验证新密码强度
- **管理员重置密码**：管理员重置用户密码时强制验证密码强度

## 配置支持

系统支持按业务系统（sysChannel）配置不同的密码强度要求，通过 `pwdStrong` 字段指定强度等级。

## 相关概念

- [[密码强度验证]]：密码强度验证机制的完整设计
- [[sso-result-code-enum]]：验证失败时返回的错误码定义
- [[sso-result-dto]]：验证结果的统一返回数据结构