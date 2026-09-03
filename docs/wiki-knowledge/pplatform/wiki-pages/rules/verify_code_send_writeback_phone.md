---
type: rule
title: 验证码发送后回写短信接收手机号
page_key: verify_code_send_writeback_phone
domain: 通知验证码短链与消息
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

本规则约束验证码发送流程：`CustVerifyCodeApplication.sendVerifyCode` 在消息类型为 PHONE 时，将 receiver 手机号通过 `contractSignInfoProvider.setVerifyContractPhone` 回写到合同签署表。

## 需求背景

验证码短信发送后，合同签署表需要记录验证码接收手机号，以便后续签署流程。相关概念 [[receiver]]、[[business_id]]、[[verify_code]]。

## 版本演进

基于 code_path:CustVerifyCodeApplication.sendVerifyCode 证据形成 v0.1 契约。

```ground:rule
name: 验证码发送后回写短信接收手机号
content: CustVerifyCodeApplication.sendVerifyCode在消息类型为PHONE时，将receiver手机号通过contractSignInfoProvider.setVerifyContractPhone回写到合同签署表
impact: 合同签署表记录验证码接收手机号
field_targets: [VerifyCodeSendReqDTO.serviceKey, VerifyCodeSendReqDTO.businessId, MessageContext.receiver]
evidence: code_path:CustVerifyCodeApplication.sendVerifyCode
```