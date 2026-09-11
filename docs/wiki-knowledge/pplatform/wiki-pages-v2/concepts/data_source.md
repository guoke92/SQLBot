---
type: concept
title: data_source
page_key: concept/data_source
domain: CA证书认证
status: draft
aliases: [数据来源]
oid: 1
scope:
  databases: [unknown]
sources: [code]
contract_version: "0.1"
maps_to: CA认证数据来源枚举
adjudication: boundary
also_confused_with: []
field_targets:
  - ca_certification_info.data_source
---

data_source 标识一条 CA 认证数据是从哪个入口产生的，落在 [[tables/ca_certification_info]] 的 data_source 字段上，取值在代码中固定为三种。

## 边界与辨析

- CHANNEL_OPENAPI：渠道 API。经该来源进入的认证在上送签章中台时，意愿认证 JSON 可豁免（见 [[rules/submit_sign_center_completeness]]）。
- FBP_PORTAL：产融门户。
- OPERATION_PLATFORM：运营中台。运营中台侧的企业名与签章中台证书登记名可能不一致，这会触发升级授权书流程（[[rules/upgrade_auth_online_seal]]）。

三个取值是互斥的入口归属，不代表数据质量或可信度差异；把它与「来源系统」（如 [[tables/ca_cfca_upgrade_report]] 的 source_system）混用会丢失粒度，后者描述上报异常来自哪个业务系统。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。三个取值的含义来自代码枚举证据。

## 版本演进

暂无文档化的版本演进证据。

相关页面：[[tables/ca_certification_info]]、[[rules/submit_sign_center_completeness]]、[[concepts/one_cert_four_steps]]。