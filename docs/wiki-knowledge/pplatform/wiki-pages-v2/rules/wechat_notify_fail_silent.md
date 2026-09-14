---
type: rule
title: 微信验证码通知失败不抛异常
page_key: wechat_notify_fail_silent
domain: notification
status: draft
aliases: [微信通知失败静默, sendVerificationCodeNotification 返回 true]
oid: 1
scope:
  databases: []
sources:
  - WechatNotificationService.java:70-80
  - reqdoc:平台基础组件业务规则文档#2.2
contract_version: "0.1"
belong: rules
---

WechatNotificationService.sendVerificationCodeNotification 捕获异常、记录日志并返回 true，调用方不会因微信通知失败而中断。与短信侧对称的规则见 [[sms_send_fail_silent]]。

## 需求背景
需求文档要求发送失败记录日志、不抛异常给业务；微信服务号通知依赖第三方接口，更需容错。

## 版本演进
- 当前返回值为 true 的语义是「已尽力发送」，不表示对方已收到，这一点在统计口径上需注意。

```ground:rule
name: 微信验证码通知失败不抛异常
content: WechatNotificationService.sendVerificationCodeNotification 捕获异常记录日志并返回 true
impact: 微信通知失败不影响主流程
field_targets: []
evidence: WechatNotificationService.java:70-80 + reqdoc:平台基础组件业务规则文档#2.2
```