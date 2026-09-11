---
type: concept
title: 线下授权（off_auth）
page_key: concept.off_auth
domain: 授权协议与电子授权
status: draft
aliases:
  - OFF_AUTH
  - 线下签署模式
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthSignOrchestrationApplication.java
contract_version: "0.1"
maps_to: "CustEnterpriseUserDTO.authModel = AuthModel.OFF_AUTH.getCode()（代码注释与日志字面为 off_auth），签署编排的硬条件之一"
field_targets: []
adjudication: boundary
also_confused_with:
  - 线上签署（on_auth）
  - 邀请认证-平台录入（业务上必然线下签署）
boundary: "authModel 是企业用户在运营中台的授权模式；与企业建档方式 identify_style 正交"
---

`off_auth` 是企业用户在运营中台的授权模式取值，作为 [[calibers/offline-electronic-auth-trigger]] 的硬条件之一出现在签署编排中（代码注释与日志字面为 `off_auth`）。

它与 [[tables/cust_company_info|identify_style]]（建档方式）正交：即使业务上「邀请认证-平台录入」往往伴随线下签署，也仍然是两个不同维度，不能互相替代判定；建档分支的白名单见 [[calibers/build-scope-identify-styles]]。

## 需求背景
只有线下授权模式的企业才需要线下授权书的电子化替代方案，线上签署企业走各自既有通道，故编排以 `authModel` 作为分流条件。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的术语桥接；本次分析未提供 document_claim（未证实主张）。