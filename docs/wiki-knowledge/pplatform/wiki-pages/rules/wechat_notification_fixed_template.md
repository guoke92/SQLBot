---
type: rule
title: 微信通知固定模板
page_key: wechat_notification_fixed_template
belong: rules
domain: 通知验证码短链与消息
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

本规则约束微信验证码通知模板：`WechatNotificationService` 发送微信验证码使用模板编号 1000001、系统代码 beehive，内容固定。

## 需求背景

微信通知是验证码发送后的触达渠道，模板固定保证通知一致性。相关规则 [[verify_code_send_wechat_notification]]。

## 版本演进

基于 code_path:WechatNotificationService.sendVerificationCodeNotification 证据形成 v0.1 契约。

```ground:rule
name: 微信通知固定模板
content: WechatNotificationService发送微信验证码使用模板编号1000001，系统代码beehive
impact: 微信通知内容固定
field_targets: [WechatSendRequest.templateNo, WechatSendRequest.sysCode]
evidence: code_path:WechatNotificationService.sendVerificationCodeNotification
```