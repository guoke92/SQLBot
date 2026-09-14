---
type: rule
title: 验证码有效期配置缺失抛异常
page_key: verify_code_period_config_require
domain: notification
status: draft
aliases: [缺少验证码有效期配置, getIndentifyConfigDTO 为空]
oid: 1
scope:
  databases: []
sources:
  - MessageFacade.java:sendVerifyCode
contract_version: "0.1"
belong: rules
---

sendVerifyCode 中若 indentifycodeFacade.getIndentifyConfigDTO 返回空，抛 CommonException「缺少验证码有效期配置」。即验证码发送强依赖有效期配置。

## 需求背景
验证码若无有效期则无法判断是否可复用，需求侧要求把有效期配置作为发送前置条件，配置缺失时快速失败而非静默发送。

## 版本演进
- 当前为抛异常失败策略；是否应降级为默认有效期，本次分析无证据。

```ground:rule
name: 验证码有效期配置缺失抛异常
content: sendVerifyCode 中若 indentifycodeFacade.getIndentifyConfigDTO 返回空，抛 CommonException 缺少验证码有效期配置
impact: 验证码发送依赖有效期配置
field_targets: []
evidence: MessageFacade.java:sendVerifyCode
```