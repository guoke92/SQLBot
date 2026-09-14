---
type: rule
title: 短信发送失败不抛异常
page_key: sms_send_fail_silent
domain: notification
status: draft
aliases: [短信失败静默, sendSmsMessage 不抛异常]
oid: 1
scope:
  databases: []
sources:
  - PlatMessageApplication.java:34-45
  - reqdoc:平台基础组件业务规则文档#2.2
contract_version: "0.1"
belong: rules
---

PlatMessageApplication.sendSmsMessage 捕获发送异常并返回 fail，不向调用方抛出。与之同构的微信侧行为见 [[wechat_notify_fail_silent]]。

## 需求背景
需求文档（平台基础组件业务规则文档 2.2）明确发送失败记录日志、不抛异常给业务；代码实现与该叙述一致。

## 版本演进
- 需求文档另提出「短信需要幂等时使用 RedisSmsLock 检查/加锁」，链路上未出现 RedisSmsLock 调用，未证实，见 REVIEW。

```ground:rule
name: 短信发送失败不抛异常
content: PlatMessageApplication.sendSmsMessage 捕获异常并返回 fail，不向调用方抛出
impact: 短信发送失败不影响主流程
field_targets: []
evidence: PlatMessageApplication.java:34-45 + reqdoc:平台基础组件业务规则文档#2.2
```