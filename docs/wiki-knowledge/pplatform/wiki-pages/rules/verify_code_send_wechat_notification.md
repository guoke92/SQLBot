---
type: rule
title: 验证码发送后触发微信服务号通知
page_key: verify_code_send_wechat_notification
domain: 通知验证码短链与消息
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

本规则约束验证码发送后的微信通知：当消息类型为 PHONE 时，`CustVerifyCodeApplication.sendVerifyCode` 调用微信通知服务发送验证码通知，实现短信与微信联动触达。

## 需求背景

通知组件以邮件/短信/微信三类抽象，微信通知是其中一个渠道。相关概念 [[notice_message]]、[[verify_code]]、[[receiver]]。

## 版本演进

基于 code_path:CustVerifyCodeApplication.sendVerifyCode + WechatNotificationService.sendVerificationCodeNotification 证据形成 v0.1 契约。

```ground:rule
name: 验证码发送后触发微信服务号通知
content: CustVerifyCodeApplication.sendVerifyCode调用wechatNotificationService.sendVerificationCodeNotification，当消息类型为PHONE时发送微信验证码通知
impact: 短信验证码发送后同时微信通知
field_targets: [MessageContext.messageType, MessageContext.receiver, MessageContext.verifyCode]
evidence: code_path:CustVerifyCodeApplication.sendVerifyCode + WechatNotificationService.sendVerificationCodeNotification
```