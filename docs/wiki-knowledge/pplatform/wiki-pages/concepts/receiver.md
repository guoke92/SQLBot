---
type: concept
title: 接收人
page_key: receiver
belong: concepts
domain: 通知验证码短链与消息
status: published
aliases: [receiver, receiverList, receiverPhone]
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
maps_to: SendMessageReq.receiverList / MessageContext.receiver
field_targets: [SendMessageReq.receiverList, MessageContext.receiver]
adjudication: boundary
also_confused_with: [signatoryId（签署人ID，用于合同签署场景）, companyId（企业ID，可能作为signatoryId默认值）]
scope:
  databases: [lowcode_pplatform]
---

接收人指实际接收消息的手机号/邮箱列表，通过 `receiverList` 或 `MessageContext.receiver` 承载。签署人 ID（signatoryId）是签署标识，发送验证码时可回写手机号。

## 需求背景

发送验证码或消息时，接收人信息用于触达目标。相关规则 [[verify_code_send_required_params_validation]]、[[verify_code_send_writeback_phone]]、[[verify_code_send_wechat_notification]]。

## 版本演进

基于语义分析 term_bridges 形成 v0.1 契约。接收人与签署人之间的转换关系在合同签署场景中体现。

（无 ground 块，符合 concept 规范）