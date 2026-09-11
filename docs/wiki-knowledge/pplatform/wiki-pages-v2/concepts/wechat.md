---
type: concept
title: 微信（企微 / 服务号 / 小程序分流）
page_key: concept/wechat
domain: 微信生态/小程序/扫脸
status: draft
aliases: [微信通知, WechatNotificationService, 企微]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:WechatNotifyFacade.java
  - code:WechatWorkMessageService.java
  - code:WechatNotificationService.java
maps_to: "需拆分：WechatNotifyFacade/WechatWorkMessageService 直连『企业微信 message/send』；WechatNotificationService（sso 组件）为另一路微信触达抽象。"
adjudication: boundary
also_confused_with:
  - 企业微信（企微）
  - 微信服务号
  - 小程序
boundary: "企微消息面向内部审批人（touser=企微 userId，textcard）；小程序链路（MiniProgramController）面向 C 端小程序，用 api.weixin.qq.com accessToken。二者接入主体与 token 体系不同。"
contract_version: "0.1"
---

# 微信（企微 / 服务号 / 小程序分流）

「微信」在本域内并非单一通道，需拆为至少两类：面向内部审批人的企业微信消息（WechatNotifyFacade / WechatWorkMessageService），以及面向 C 端的小程序链路（MiniProgramController）。另有 sso 组件的 WechatNotificationService 抽象。

## 需求背景

内部通知与 C 端刷脸接入主体、凭证体系不同，必须分流建模，否则会误把企微凭证用于小程序调用。

## 版本演进

v0.1 明确三类触达通道的边界。

## 边界说明

企微消息用企微 userId（touser）+ textcard；小程序链路用 api.weixin.qq.com accessToken（见 [[access_token]]）。

相关：[[wx_work_user]]、[[wecom_active_member]]、[[access_token]]、[[miniprogram_qrcode]]。