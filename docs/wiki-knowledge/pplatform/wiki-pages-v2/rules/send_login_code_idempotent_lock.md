---
type: rule
title: 验证码发送幂等锁
page_key: send_login_code_idempotent_lock
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 登录验证码发送限频
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:sendLoginCode
contract_version: "0.1"
belong: rules
---

登录验证码发送以场景 + 业务 id 为 key 抢锁，实现幂等与限频，并在手机号为空时自动降级为邮箱场景。

## 需求背景

短信/邮件发送需要幂等与场景自动降级：LANDED_PHONE→LANDED_EMAIL、resetpassword→resetpasswordemail，
涉及 [[sys_user.mobile]] 与 [[sys_user.email]]。

## 版本演进

- v0（草稿）：规则来自代码锁与场景切换实现。

```ground:rule
name: 验证码发送幂等锁
content: "sendLoginCode 以 scenesType+businessId 作为 key 抢 RedisSmsLock，抢不到抛“调用频率过快”；手机号为空时按场景切换为邮箱场景（LANDED_PHONE→LANDED_EMAIL、resetpassword→resetpasswordemail）。"
impact: "短信/邮件发送幂等与场景自动降级。"
field_targets:
  - sys_user.mobile
  - sys_user.email
evidence: "code_path:SaaSAuthController.java:sendLoginCode"
```

相关：[[sys_user]]、[[update_agw_login_email]]。