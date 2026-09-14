---
type: rule
title: 微信验证码通知模板固定
page_key: wechat_verify_code_template_fixed
domain: notification
status: draft
aliases: [templateNo 1000001, sysCode beehive]
oid: 1
scope:
  databases: []
sources:
  - WechatNotificationService.java:TemplateNo
  - WechatNotificationService.java:SysCode
contract_version: "0.1"
belong: rules
---

微信验证码通知固定使用 sysCode=beehive、templateNo=1000001，dataMap 含 phone_number、code、system_name 三个变量。

## 需求背景
微信服务号模板消息需预先报备，需求侧要求验证码类通知统一使用同一模板，便于模板审核与运维。

## 版本演进
- 模板号当前硬编码；若更换模板需同步发布，且涉及已报备模板的替换。

```ground:rule
name: 微信验证码通知模板固定
content: 微信验证码通知使用 sysCode=beehive，templateNo=1000001，dataMap 含 phone_number/code/system_name
impact: 固定短信/企微验证码模板
field_targets: []
evidence: WechatNotificationService.java:TemplateNo/SysCode
```