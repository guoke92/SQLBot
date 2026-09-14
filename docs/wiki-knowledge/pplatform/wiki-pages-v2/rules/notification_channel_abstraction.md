---
type: rule
title: 通知通道三类抽象
page_key: notification_channel_abstraction
domain: notification
status: draft
aliases: [通知组件通道抽象, 邮件短信微信]
oid: 1
scope:
  databases: []
sources:
  - MessageFacade.java:MessageTypeEnum
  - WechatNotificationService.java:1
  - reqdoc:平台基础组件业务规则文档#2.2
contract_version: "0.1"
belong: rules
---

通知组件以邮件、短信、微信三类通道抽象承载各类触达场景，业务侧按场景选择通道，通道实现各自封装发送细节。验证码场景的选择见 [[verify_code_scenes_whitelist]]，站内信与下游路由见 [[notice_local_downstream_route]]。

## 需求背景
需求文档（平台基础组件业务规则文档 2.2）要求通知能力以通道抽象方式提供，避免业务方直接依赖具体供应商接口；代码侧 MessageTypeEnum 与 WechatNotificationService 与该叙述一致。

## 版本演进
- 当前抽象为三类通道；后续若新增通道类型，本页与通道相关规则需同步。

```ground:rule
name: 通知通道三类抽象
content: 通知组件以邮件/短信/微信三类抽象承载触达场景
impact: 决定业务侧按场景选择通道的调用方式
field_targets: []
evidence: MessageFacade.java:MessageTypeEnum + WechatNotificationService.java:1 + reqdoc:平台基础组件业务规则文档#2.2
```