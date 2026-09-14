---
type: rule
title: 合同签署验证码多笔限制
page_key: contract_sign_verify_code_multi_limit
domain: notification
status: draft
aliases: [多笔限制, sendVerifyCode 入参限制]
oid: 1
scope:
  databases: []
sources:
  - CustVerifyCodeController.java:sendVerifyCode
contract_version: "0.1"
belong: rules
---

CustVerifyCodeController.sendVerifyCode 中 serviceKey 与 businessId 不能同时为多笔，否则抛异常，用于限制批量签署验证码的入参组合。

## 需求背景
批量签署与单笔签署的验证码归属不同，需求侧要求禁止两种多笔标识同时传入，避免验证码无法定位到唯一业务对象。

## 版本演进
- 当前为入参校验；批量签署场景的具体处理见 [[verify_code_scenes_whitelist]]。

```ground:rule
name: 合同签署验证码多笔限制
content: CustVerifyCodeController.sendVerifyCode 中 serviceKey 与 businessId 不能同时为多笔，否则抛异常
impact: 限制批量签署验证码入参组合
field_targets: []
evidence: CustVerifyCodeController.java:sendVerifyCode
```