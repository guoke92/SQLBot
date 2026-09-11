---
type: entity
title: sso_user表
created: 2026-08-28
updated: 2026-08-28
tags: [SSO, 数据库表, 用户管理, BCrypt]
related: [sso-user-pwd-history, sso-user-system, sso-user-login-history, 用户信息与身份鉴别信息分离存储, 登录失败计数与账户锁定, 密码过期策略]
sources: ["需求文档/SSO单点登录系统安全设计文档.docx"]
---

# sso_user表

## 概述

sso_user 是SSO单点登录系统的用户基本信息表，存储用户基本信息及加密后的密码（BCrypt哈希值）和密码相关元数据。

## 字段定义

| 字段 | 说明 |
|------|------|
| sso_id | 主键，用户唯一标识 |
| login_name | 登录名 |
| user_name | 用户姓名 |
| phone | 手机号码 |
| email | 电子邮箱 |
| password | 加密后的密码（BCrypt哈希值） |
| pwd_update_time | 密码最后更新时间 |
| pwd_is_locked | 账户是否被锁定 |
| pwd_locked_time | 账户锁定截止时间 |
| login_fail_count | 连续登录失败次数 |

## 关联关系

- 通过 `sso_id` 关联 [[sso-user-pwd-history]]（密码历史表）
- 通过 `sso_id` 关联 [[sso-user-system]]（用户系统关联表）
- 通过 `sso_id` 关联 [[sso-user-login-history]]（登录历史表）

## 安全设计

根据 [[用户信息与身份鉴别信息分离存储]] 的设计原则，sso_user 表虽然存储了密码哈希值，但密码历史记录独立存储在 [[sso-user-pwd-history]] 中，实现物理和逻辑分离。

密码相关元数据（pwd_is_locked、pwd_locked_time、login_fail_count）用于支持 [[登录失败计数与账户锁定]] 机制；pwd_update_time 用于支持 [[密码过期策略]] 检查。

## 相关概念

- [[用户信息与身份鉴别信息分离存储]]：数据分离存储的设计原则
- [[bcrypt加密存储]]：密码加密存储的技术方案
- [[登录失败计数与账户锁定]]：利用该表字段实现的锁定机制
- [[密码过期策略]]：利用pwd_update_time实现的过期检查