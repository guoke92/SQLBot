---
type: concept
title: 平台产品编码 PLATFORM
page_key: platform-product-code
domain: 授权协议与电子授权
status: draft
aliases:
  - 平台级授权书
  - PLATFORM_PRODUCT_TYPE
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthAgreementDomainService.java
  - db:authorization_agreement
contract_version: "0.1"
maps_to: "authorization_agreement.platform_product_code = 'PLATFORM'，表示平台级授权而非某个业务产品的存量授权"
field_targets:
  - authorization_agreement.platform_product_code
adjudication: boundary
also_confused_with:
  - 业务产品编码（ACFLOW/AMS/ORDER/RVSFACTOR_PC…）
boundary: "是否补签只看 PLATFORM 行；具体产品行的 Y 表示存量系统已授权，用于免补签判定"
sources: ["enrich:wiki-admin"]
belong: concepts
---

`PLATFORM`（代码常量 `PLATFORM_PRODUCT_TYPE`）是 [[tables/authorization_agreement]] 中 `platform_product_code` 的一个特殊取值，标记该行为平台级授权。是否已授权、是否需要补签只考察该行，见 [[calibers/platform-level-authed]]。

与业务产品编码（ACFLOW/AMS/ORDER/RVSFACTOR_PC…）的边界：产品行的 `authed_status='Y'` 表示存量系统已授权，用于免补签判定，但不代表平台级授权已完成。混用两者会导致对企业重复要求签署。

## 需求背景
存量系统的授权记录按产品分散，而平台级授权是唯一免签依据，因此需要用同一字段上的特殊取值区分两个层级，避免新增冗余字段。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的术语桥接；本次分析未提供 document_claim（未证实主张）。

相关：[[authorization_agreement]]
