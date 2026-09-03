---
type: concept
title: 业务ID
page_key: business_id
domain: 通知验证码短链与消息
status: published
aliases: [businessId, businessType]
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
maps_to: SendMessageReq.businessId / businessType
field_targets: [SendMessageReq.businessId, SendMessageReq.businessType]
adjudication: boundary
also_confused_with: [cust_company_info（企业ID）与 cust_person_info（个人ID）作为businessId时实体不同, PlatMessageDto.businessId（短信业务ID）]
scope:
  databases: [lowcode_pplatform]
---

业务ID是消息发送的业务对象标识，具体含义由 `businessType` 定义，常见值为 `cust_company_info` 或 `cust_person_info`。它不等同于短信平台业务 ID，需按上下文区分。

## 需求背景

发送消息或验证码时，业务 ID 用于定位业务对象，例如合同签署场景中 businessId 可能为企业或个人。相关规则 [[verify_code_send_writeback_phone]]、[[contract_sign_verify_code_multi_limit]]。

## 版本演进

基于语义分析 term_bridges 形成 v0.1 契约。业务 ID 的具体枚举语义在本主题中未完全展开。

（无 ground 块，符合 concept 规范）