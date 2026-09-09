---
type: rule
title: 验证码发送必需参数校验
page_key: verify_code_send_required_params_validation
belong: rules
domain: 通知验证码短链与消息
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

本规则约束验证码发送入口参数：`MessageFacade.sendVerifyCode` 校验 receiver、dbTenantCode、paramMap 均不能为空，否则抛出 BaseException，保证发送数据完整。

## 需求背景

发送验证码前必须保证必要数据存在。相关概念 [[receiver]]、[[verify_code]]。

## 版本演进

基于 code_path:MessageFacade.sendVerifyCode 证据形成 v0.1 契约。

```ground:rule
name: 验证码发送必需参数校验
content: MessageFacade.sendVerifyCode中校验：receiver不能为空、dbTenantCode不能为空、paramMap不能为空，否则抛BaseException
impact: 保证验证码发送数据完整
field_targets: [MessageContextPramDTO.receiver, MessageContextPramDTO.dbTenantCode, MessageContextPramDTO.paramMap]
evidence: code_path:MessageFacade.sendVerifyCode
```