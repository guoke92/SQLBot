---
type: rule
title: 合同签署验证码多笔限制
page_key: contract_sign_verify_code_multi_limit
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

本规则约束合同签署验证码发送：`CustVerifyCodeController.sendVerifyCode` 校验 `serviceKey` 和 `businessId` 不能同时为多笔，防止批量发送验证码冲突。

## 需求背景

合同签署验证码发送固定使用 SMS_BATCH_SIGN_CONTRACT 场景，但需限制多笔冲突。相关概念 [[business_id]]、[[verify_code]]。reqdoc claim 已确认。

## 版本演进

基于 code_path:CustVerifyCodeController.sendVerifyCode 及 code_path:MessageFacade.sendVerifyCode 的 reqdoc 证据形成 v0.1 契约。

```ground:rule
name: 合同签署验证码多笔限制
content: CustVerifyCodeController.sendVerifyCode校验：serviceKey和businessId不能同时为多笔
impact: 防止批量发送验证码冲突
field_targets: [VerifyCodeSendReqDTO.serviceKey, VerifyCodeSendReqDTO.businessId]
evidence: code_path:CustVerifyCodeController.sendVerifyCode + reqdoc:合同签署验证码发送固定使用SMS_BATCH_SIGN_CONTRACT场景
```