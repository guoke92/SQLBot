---
type: rule
title: 验证码场景白名单
page_key: verify_code_scenes_whitelist
domain: notification
status: draft
aliases: [VERIFY_CODE_SCENES, 验证码场景]
oid: 1
scope:
  databases: []
sources:
  - MessageFacade.java:VERIFY_CODE_SCENES
contract_version: "0.1"
belong: rules
---

MessageFacade.VERIFY_CODE_SCENES 指定需要走 sendVerifyCode 的场景：批量签署、落地手机、重置密码、注册手机、法人授权、客户建档认证、CA 意向确认。其余场景不生成验证码。相关的有效期依赖见 [[verify_code_period_config_require]]，落库回填见 [[verify_code_phone_writeback]]。

## 需求背景
验证码有短信成本与骚扰风险，需求侧要求按场景白名单开放，避免任意业务调用验证码能力。

## 版本演进
- 白名单当前为代码常量，新增场景需要改代码并发布；表 cust_message_send_policy 的场景开关与白名单的关系在本分析中无证据。

```ground:rule
name: 验证码场景白名单
content: MessageFacade.VERIFY_CODE_SCENES 指定需要走 sendVerifyCode 的场景：批量签署、落地手机、重置密码、注册手机、法人授权、客户建档认证、CA意向确认
impact: 决定是否生成并注入验证码
field_targets: []
evidence: MessageFacade.java:VERIFY_CODE_SCENES
```