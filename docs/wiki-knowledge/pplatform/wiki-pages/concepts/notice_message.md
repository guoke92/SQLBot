---
type: concept
title: 通知/消息
page_key: notice_message
domain: 通知验证码短链与消息
status: published
aliases: [通知, 消息, 站内信, Notice, Message, 短信]
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
maps_to: MessageFacade / MessageSendProvider / NoticeProvider
field_targets: []
adjudication: boundary
also_confused_with: [NoticeProvider（站内信）与 MessageSendProvider（短信/邮件等）渠道不同, MessageTypeEnum.PHONE/EMAIL/NOTICE 渠道区分]
scope:
  databases: [lowcode_pplatform]
---

“通知/消息”泛指消息触达，按渠道分为站内信、短信、邮件、微信；不同 Provider 负责不同渠道。其边界是渠道差异，而非统一实体。

## 需求背景

通知组件以邮件/短信/微信三类抽象，承载客户邀请、改密、批量签约等触达场景（已确认 reqdoc claim）。消息发送失败时记录日志不抛异常给业务（对应规则 [[sms_send_exception_not_throw]]）。异步邮件 @Async 提交线程池在给定代码中未见，待 REVIEW。

## 版本演进

本页基于语义分析 term_bridges 形成 v0.1 契约。渠道映射与发送失败不抛异常已确认，异步邮件实现待确认。

（无 ground 块，符合 concept 规范）