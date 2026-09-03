---
type: rule
title: 短信发送异常不抛给调用方
page_key: sms_send_exception_not_throw
domain: 通知验证码短链与消息
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

本规则约束短信发送异常处理：`PlatMessageApplication.sendSmsMessage` 捕获所有异常，记录日志并返回失败响应，调用方收到失败响应而非异常。

## 需求背景

消息发送失败时记录日志，不抛异常给业务，这是通知组件的基本约定。相关概念 [[notice_message]]。

## 版本演进

基于 code_path:PlatMessageApplication.sendSmsMessage 证据形成 v0.1 契约。同时 reqdoc claim“消息发送失败时记录日志，不抛异常给业务”已确认并双源锚定。

```ground:rule
name: 短信发送异常不抛给调用方
content: PlatMessageApplication.sendSmsMessage捕获所有异常，记录日志并返回PlatMessageRespDto.fail(e.getMessage())
impact: 调用方收到失败响应而非异常
field_targets: [SendMessageReq, PlatMessageRespDto]
evidence: code_path:PlatMessageApplication.sendSmsMessage + reqdoc:消息发送失败时记录日志，不抛异常给业务
```